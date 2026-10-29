"""Gera as conversas de exemplo pedidas no enunciado, em Markdown.

    uv run python -m chatbot_python.exemplos > docs/exemplos_q2.md

Roda duas conversas reais contra o provedor configurado em `LLM_MODEL` (custa centavos):
uma sem RAG, mostrando a memória entre perguntas e o escopo, e uma com RAG + tutor,
mostrando as ferramentas. Cada resposta vem com a contagem de tokens.
"""

import re
import sys
from datetime import date

import openai

from .agent import criar_agente, criar_modelo, perguntar
from .settings import settings

CONVERSA_BASICA = [
    "Como criar uma lista em Python?",
    "E como adiciono um item nela?",  # depende do histórico: "nela" = a lista
    "Qual a diferença entre lista e tupla?",
    "Como leio um arquivo CSV e somo uma coluna?",
    "O que é list comprehension e quando não devo usar?",
    "Me dá uma receita de bolo de cenoura?",  # fora de escopo
]

CONVERSA_RAG = [
    "O que é RAG e por que reduz alucinações?",
    "Quando um chatbot de tutoria deve passar a dúvida para uma pessoa?",
    "Quero falar com um tutor humano sobre a nota da minha prova.",
]


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def _conversa(titulo: str, perguntas: list[str], **opcoes) -> int:
    agente = criar_agente(**opcoes)
    thread_id = _slug(titulo)
    total_tokens = 0
    print(f"\n## {titulo}\n")
    print(f"Opções: `{opcoes}` · thread `{thread_id}`\n")
    for pergunta in perguntas:
        resposta = perguntar(agente, pergunta, thread_id)
        total_tokens += resposta.tokens_total
        ferramentas = ", ".join(resposta.ferramentas_usadas) or "nenhuma"
        print(f"**Você:** {pergunta}\n")
        print(f"**Tutor:**\n\n{resposta.texto}\n")
        print(
            f"<sub>tokens: {resposta.tokens_entrada} entrada + {resposta.tokens_saida} saída"
            f" · ferramentas: {ferramentas}</sub>\n\n---\n"
        )
    print(f"Total da conversa: {total_tokens} tokens.\n")
    return total_tokens


def main() -> None:
    try:
        criar_modelo()  # valida LLM_MODEL e a chave antes de imprimir qualquer coisa
    except (ValueError, RuntimeError) as erro:
        sys.exit(str(erro))
    print("# Exemplos de perguntas e respostas (Questão 2)\n")
    print(
        f"Gerado em {date.today().isoformat()} com `{settings.llm_model}` via "
        "`uv run python -m chatbot_python.exemplos`. Respostas reais, sem edição.\n"
    )
    try:
        total = _conversa("Conversa 1: memória e escopo", CONVERSA_BASICA, com_tutor=False)
        total += _conversa("Conversa 2: RAG e encaminhamento", CONVERSA_RAG, com_rag=True)
    except openai.APIError as erro:
        # Mensagem curta no stderr; o Markdown parcial já impresso fica evidente como incompleto.
        sys.exit(f"Erro na API de {settings.provedor} ({erro.__class__.__name__}): {erro.message}")
    print(f"\nTotal geral: {total} tokens.")


if __name__ == "__main__":
    main()
