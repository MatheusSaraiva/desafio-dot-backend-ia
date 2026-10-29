"""Ferramentas (tools) que o agente pode chamar.

- `criar_tool_base_conhecimento`: busca semântica da Questão 3 como ferramenta (RAG).
- `encaminhar_para_tutor`: simula o handoff para um tutor humano (mediação híbrida).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from langchain.tools import tool

from busca_semantica.search import Buscador


def criar_tool_base_conhecimento(buscador: Buscador, k: int = 4):
    """Fecha o buscador dentro da tool: o agente só vê `consultar_base_conhecimento(pergunta)`.

    `k` conta chunks, não documentos. Agrupar por documento (o padrão da busca para
    humanos) jogava fora a segunda parte de um artigo mesmo quando era ela que tinha a
    resposta: para "o que é RAG", o chunk com a definição era o 2º melhor do índice e não
    chegava ao modelo. O limiar de relevância fica no buscador (`score_minimo`): quando
    nada passa, a tool diz isso ao modelo em vez de entregar trechos irrelevantes.
    """

    @tool
    def consultar_base_conhecimento(pergunta: str) -> str:
        """Busca trechos relevantes em artigos sobre Python e educação corporativa com IA.

        Use para perguntas conceituais ("o que é", "como funciona", "quando usar").
        Retorna os trechos mais parecidos com a pergunta, cada um com o título da fonte.
        """
        resultados = buscador.buscar(pergunta, k=k, agrupar_por_documento=False)
        if not resultados:
            return "Nenhum trecho relevante encontrado na base de conhecimento."
        # Formato simples e estável: o modelo lê e cita os títulos. Sem score: o RRF da
        # busca híbrida não é uma similaridade e só confundiria o modelo.
        blocos = [
            f"[{i}] Fonte: {r.titulo} (trecho {r.indice_chunk + 1})\n{r.trecho}"
            for i, r in enumerate(resultados, start=1)
        ]
        return "\n\n".join(blocos)

    return consultar_base_conhecimento


@dataclass
class RegistroHandoff:
    ticket: int
    motivo: str
    criado_em: datetime


@dataclass
class FilaDeTutores:
    """Registro em memória dos encaminhamentos.

    Em produção isso viraria um ticket no sistema de mediação (fila + notificação ao
    tutor, com o histórico da conversa anexado). Aqui basta provar o fluxo.
    """

    registros: list[RegistroHandoff] = field(default_factory=list)

    def registrar(self, motivo: str) -> RegistroHandoff:
        registro = RegistroHandoff(len(self.registros) + 1, motivo, datetime.now(UTC))
        self.registros.append(registro)
        return registro

    def limpar(self) -> None:
        self.registros.clear()


fila_de_tutores = FilaDeTutores()


@tool
def encaminhar_para_tutor(motivo: str) -> str:
    """Encaminha a conversa para um tutor humano.

    Use quando a pessoa pedir para falar com um humano, quando a dúvida envolver notas,
    prazos ou avaliação, ou quando você não conseguir ajudar com segurança.
    `motivo` deve resumir em uma frase por que o encaminhamento é necessário.
    """
    registro = fila_de_tutores.registrar(motivo)
    return (
        f"Encaminhado para a tutoria humana (ticket #{registro.ticket}). Motivo: {motivo}. "
        "Avise a pessoa que um tutor responderá em até 24 horas úteis e que ela pode "
        "continuar tirando dúvidas de Python por aqui enquanto isso."
    )
