"""Testes da Questão 2 (chatbot).

O modelo da OpenAI é substituído por `GenericFakeChatModel`, que devolve respostas
roteirizadas (texto ou chamadas de ferramenta). Assim os testes rodam sem chave, sem
rede e sem custo, e exercitam o que é nosso: montagem do agente, memória por thread,
ferramentas, validações e métricas. O teste de integração real fica marcado.
"""

import os

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolCall
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

from busca_semantica.config import settings as busca_settings
from busca_semantica.embeddings import FakeEmbedder
from busca_semantica.search import BuscadorSemantico, construir_indice
from chatbot_python.agent import criar_agente, criar_modelo, perguntar, validar_pergunta
from chatbot_python.settings import ChatSettings
from chatbot_python.tools import criar_tool_base_conhecimento, fila_de_tutores


class ModeloFalso(GenericFakeChatModel):
    """Modelo roteirizado que aceita tools (o agente chama `bind_tools` ao ser montado).

    As tools são ignoradas: as chamadas de ferramenta vêm do próprio roteiro.
    """

    def bind_tools(self, tools, **kwargs):
        return self


def modelo_falso(*respostas) -> ModeloFalso:
    """Cada chamada ao modelo consome a próxima resposta do roteiro."""
    return ModeloFalso(messages=iter(respostas))


def chamada_de_ferramenta(nome: str, **args) -> AIMessage:
    return AIMessage(content="", tool_calls=[ToolCall(name=nome, args=args, id="call_1")])


@pytest.fixture(autouse=True)
def fila_limpa():
    fila_de_tutores.limpar()
    yield
    fila_de_tutores.limpar()


# ---------------------------------------------------------------- resposta e memória


def test_responde_pergunta_simples():
    agente = criar_agente(modelo_falso("Use colchetes: `lista = []`."), com_tutor=False)

    resposta = perguntar(agente, "Como criar uma lista em Python?", thread_id="t1")

    assert "colchetes" in resposta.texto
    assert resposta.thread_id == "t1"
    assert resposta.ferramentas_usadas == []


def test_memoria_e_mantida_por_thread():
    agente = criar_agente(modelo_falso("r1", "r2", "r3"), com_tutor=False)

    perguntar(agente, "Como criar uma lista?", thread_id="a")
    perguntar(agente, "E como adiciono um item nela?", thread_id="a")
    perguntar(agente, "Olá", thread_id="b")

    historico_a = agente.get_state({"configurable": {"thread_id": "a"}}).values["messages"]
    historico_b = agente.get_state({"configurable": {"thread_id": "b"}}).values["messages"]
    assert [m.type for m in historico_a] == ["human", "ai", "human", "ai"]
    assert [m.type for m in historico_b] == ["human", "ai"]


def test_resposta_acumula_tokens_reportados_pelo_modelo():
    mensagem = AIMessage(
        content="ok",
        usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
    )
    agente = criar_agente(modelo_falso(mensagem), com_tutor=False)

    resposta = perguntar(agente, "oi", thread_id="t")

    assert (resposta.tokens_entrada, resposta.tokens_saida, resposta.tokens_total) == (12, 3, 15)


# ---------------------------------------------------------------- validações e custo


@pytest.mark.parametrize("pergunta", ["", "   "])
def test_pergunta_vazia_e_rejeitada(pergunta):
    with pytest.raises(ValueError, match="vazia"):
        validar_pergunta(pergunta)


def test_pergunta_muito_longa_e_rejeitada():
    with pytest.raises(ValueError, match="muito longa"):
        validar_pergunta("x" * 10, limite=5)


@pytest.mark.parametrize(
    ("llm_model", "variavel"),
    [("openai:gpt-5.4-mini", "OPENAI_API_KEY"), ("deepseek:deepseek-flash", "DEEPSEEK_API_KEY")],
)
def test_sem_chave_da_erro_claro(llm_model, variavel):
    config = ChatSettings(
        _env_file=None, llm_model=llm_model, openai_api_key=None, deepseek_api_key=None
    )

    with pytest.raises(RuntimeError, match=variavel):
        criar_modelo(config)


@pytest.mark.parametrize("llm_model", ["gpt-5.4-mini", "mistral:x", "openai:"])
def test_llm_model_fora_do_formato_provedor_modelo_da_erro(llm_model):
    config = ChatSettings(_env_file=None, llm_model=llm_model, openai_api_key="x")

    with pytest.raises(ValueError, match="provedor:modelo"):
        criar_modelo(config)


def test_modelo_openai_recebe_controles_de_custo():
    config = ChatSettings(
        _env_file=None,
        llm_model="openai:gpt-5.4-mini",
        openai_api_key="chave-de-teste",
        max_tokens=321,
        max_retries=1,
    )

    modelo = criar_modelo(config)

    assert isinstance(modelo, ChatOpenAI)
    assert modelo.model_name == "gpt-5.4-mini"
    assert modelo.max_tokens == 321
    assert modelo.max_retries == 1


def test_modelo_deepseek_usa_o_pacote_oficial():
    config = ChatSettings(
        _env_file=None,
        llm_model="deepseek:deepseek-flash",
        deepseek_api_key="chave-de-teste",
        max_tokens=123,
    )

    modelo = criar_modelo(config)

    assert isinstance(modelo, ChatDeepSeek)
    assert modelo.model_name == "deepseek-flash"
    assert modelo.max_tokens == 123
    assert "api.deepseek.com" in modelo.api_base


# ---------------------------------------------------------------- ferramentas


def test_encaminha_para_tutor_quando_o_modelo_pede():
    roteiro = modelo_falso(
        chamada_de_ferramenta("encaminhar_para_tutor", motivo="pediu um humano"),
        "Encaminhei você para a tutoria; respondem em até 24h.",
    )
    agente = criar_agente(roteiro, com_tutor=True)

    resposta = perguntar(agente, "Quero falar com uma pessoa.", thread_id="t")

    assert resposta.ferramentas_usadas == ["encaminhar_para_tutor"]
    assert "24h" in resposta.texto
    assert len(fila_de_tutores.registros) == 1
    assert fila_de_tutores.registros[0].motivo == "pediu um humano"


def test_rag_consulta_a_busca_semantica_da_questao_3():
    embedder = FakeEmbedder()
    buscador = BuscadorSemantico(construir_indice(busca_settings.corpus_dir, embedder), embedder)
    tool_rag = criar_tool_base_conhecimento(buscador, k=2)

    trechos = tool_rag.invoke({"pergunta": "criar lista e adicionar itens com append"})

    assert "Fonte: Listas em Python" in trechos
    assert trechos.count("Fonte:") == 2


def test_agente_usa_o_rag_e_cita_a_fonte_no_fluxo():
    embedder = FakeEmbedder()
    buscador = BuscadorSemantico(construir_indice(busca_settings.corpus_dir, embedder), embedder)
    roteiro = modelo_falso(
        chamada_de_ferramenta("consultar_base_conhecimento", pergunta="criar lista append"),
        "Use `append`.\n\nFontes: Listas em Python",
    )
    # Mesmo agente da produção, mas com a tool construída sobre o índice simulado.
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver

    agente = create_agent(
        roteiro,
        tools=[criar_tool_base_conhecimento(buscador)],
        system_prompt="teste",
        checkpointer=InMemorySaver(),
    )

    resposta = perguntar(agente, "Como adiciono itens em uma lista?", thread_id="t")

    assert resposta.ferramentas_usadas == ["consultar_base_conhecimento"]
    assert "Fontes:" in resposta.texto


# ---------------------------------------------------------------- integração real


@pytest.mark.integration
def test_integracao_openai_responde_sobre_listas():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY não definida")
    agente = criar_agente(com_tutor=False)

    resposta = perguntar(agente, "Como criar uma lista em Python? Responda em 3 linhas.", "it")

    assert "[" in resposta.texto
    assert resposta.tokens_total > 0
