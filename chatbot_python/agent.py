"""Construção do agente (LangChain v1) e função de pergunta/resposta.

Fluxo de uma pergunta:
    texto do usuário -> agente (modelo OpenAI + tools opcionais + memória por thread)
                     -> resposta em texto + métricas (tokens, ferramentas usadas)

A memória de conversa é um checkpointer do LangGraph: cada `thread_id` guarda o próprio
histórico, então duas sessões não se misturam. `InMemorySaver` vive só no processo;
em produção trocaríamos por um checkpointer persistente (MongoDB/Postgres) sem mudar
o resto do código.
"""

from dataclasses import dataclass, field

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import traceable

from .prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_RAG, SYSTEM_PROMPT_TUTOR
from .settings import PROVEDORES, ChatSettings, settings
from .tools import criar_tool_base_conhecimento, encaminhar_para_tutor


@dataclass
class Resposta:
    texto: str
    thread_id: str
    tokens_entrada: int = 0
    tokens_saida: int = 0
    ferramentas_usadas: list[str] = field(default_factory=list)

    @property
    def tokens_total(self) -> int:
        return self.tokens_entrada + self.tokens_saida


def criar_modelo(config: ChatSettings = settings) -> BaseChatModel:
    """Modelo de chat do provedor escolhido em `LLM_MODEL`, com os controles de custo.

    `init_chat_model` resolve o pacote certo a partir do prefixo (`openai:` -> ChatOpenAI,
    `deepseek:` -> ChatDeepSeek) e repassa os mesmos parâmetros; trocar de provedor é
    só mudar a variável de ambiente.
    """
    provedor, nome = config.provedor, config.nome_do_modelo
    if provedor not in PROVEDORES or not nome:
        suportados = ", ".join(f"{p}:<modelo>" for p in PROVEDORES)
        raise ValueError(
            f"LLM_MODEL='{config.llm_model}' inválido. Use o formato provedor:modelo "
            f"({suportados}); ex.: openai:gpt-5.4-mini ou deepseek:deepseek-flash."
        )
    chave = config.chave_do_provedor()
    if chave is None:
        raise RuntimeError(
            f"{PROVEDORES[provedor]} não configurada. Copie .env.example para .env e preencha."
            + config.dica_de_alternativa()
        )
    return init_chat_model(
        nome,
        model_provider=provedor,
        api_key=chave,
        max_tokens=config.max_tokens,
        timeout=config.timeout_segundos,
        max_retries=config.max_retries,
        # Pede a contagem de tokens também no streaming (o CLI mostra ao fim da resposta).
        stream_usage=True,
    )


def criar_agente(
    modelo: BaseChatModel | None = None,
    *,
    com_rag: bool = False,
    com_tutor: bool = True,
    checkpointer: BaseCheckpointSaver | None = None,
):
    """Monta o agente. Sem tools ele é um chatbot puro; com tools vira um agente ReAct.

    - `com_rag`: adiciona a busca semântica da Questão 3 como ferramenta (exige índice).
    - `com_tutor`: adiciona o encaminhamento para tutor humano.
    - `modelo`: permite injetar um modelo falso nos testes (sem chave, sem custo).
    """
    tools = []
    system_prompt = SYSTEM_PROMPT
    if com_rag:
        # Import tardio: só carrega o índice/modelo de embeddings quando o RAG é pedido.
        from busca_semantica.config import settings as busca_settings
        from busca_semantica.hybrid import BuscadorHibrido
        from busca_semantica.search import carregar_buscador

        # Busca híbrida (semântica + BM25): foi a que mediu melhor na avaliação da Q3.
        # O limiar vem da configuração da busca, calibrado para o modelo de embeddings.
        semantico = carregar_buscador(score_minimo=busca_settings.score_minimo)
        tools.append(
            criar_tool_base_conhecimento(BuscadorHibrido(semantico), k=settings.rag_trechos)
        )
        system_prompt += SYSTEM_PROMPT_RAG
    if com_tutor:
        tools.append(encaminhar_para_tutor)
        system_prompt += SYSTEM_PROMPT_TUTOR

    return create_agent(
        modelo or criar_modelo(),
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer or InMemorySaver(),
    )


def _mensagens_do_turno(mensagens: list[BaseMessage]) -> list[BaseMessage]:
    """Só as mensagens geradas depois da última pergunta do usuário (o histórico vem junto)."""
    for i in range(len(mensagens) - 1, -1, -1):
        if isinstance(mensagens[i], HumanMessage):
            return mensagens[i + 1 :]
    return mensagens


def validar_pergunta(pergunta: str, limite: int = settings.tamanho_maximo_pergunta) -> str:
    pergunta = pergunta.strip()
    if not pergunta:
        raise ValueError("A pergunta está vazia.")
    if len(pergunta) > limite:
        raise ValueError(f"Pergunta muito longa ({len(pergunta)} caracteres; limite {limite}).")
    return pergunta


@traceable(name="perguntar", run_type="chain")
def perguntar(agente, pergunta: str, thread_id: str) -> Resposta:
    """Envia uma pergunta ao agente dentro de uma conversa (`thread_id`) e resume o resultado.

    Decorado com `@traceable`: com LANGSMITH_TRACING=true cada pergunta vira um trace no
    LangSmith, com as chamadas ao modelo e às ferramentas aninhadas.
    """
    pergunta = validar_pergunta(pergunta)
    config = {"configurable": {"thread_id": thread_id}}
    estado = agente.invoke({"messages": [HumanMessage(content=pergunta)]}, config)

    turno = _mensagens_do_turno(estado["messages"])
    # `.text` junta só os blocos de texto da mensagem (ignora blocos de tool call).
    resposta = Resposta(texto=turno[-1].text if turno else "", thread_id=thread_id)
    for mensagem in turno:
        if isinstance(mensagem, AIMessage):
            uso = mensagem.usage_metadata or {}
            resposta.tokens_entrada += uso.get("input_tokens", 0)
            resposta.tokens_saida += uso.get("output_tokens", 0)
        elif isinstance(mensagem, ToolMessage) and mensagem.name:
            resposta.ferramentas_usadas.append(mensagem.name)
    return resposta
