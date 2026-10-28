"""Chatbot no terminal.

    uv run python -m chatbot_python.cli                       # conversa interativa
    uv run python -m chatbot_python.cli --pergunta "Como criar uma lista em Python?"
    uv run python -m chatbot_python.cli --rag                 # com a busca semântica da Q3

Comandos dentro da conversa: /novo (zera o histórico), /sair.
"""

import os
import uuid
from collections.abc import Callable
from typing import Annotated

import openai
import typer
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import criar_agente, perguntar, validar_pergunta
from .settings import settings

console = Console()
# pretty_exceptions_show_locals=False: um traceback com variáveis locais poderia imprimir
# a chave da API no terminal (ou num log colado em um ticket).
app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)


def _mensagem_de_erro_da_api(erro: openai.APIError) -> str:
    """Erros da OpenAI em uma linha, sem traceback e sem ecoar segredos."""
    if isinstance(erro, openai.AuthenticationError):
        return "Chave da OpenAI inválida (401). Confira OPENAI_API_KEY no .env."
    if isinstance(erro, openai.NotFoundError):
        return f"Modelo '{settings.openai_model}' não encontrado. Ajuste OPENAI_MODEL no .env."
    if isinstance(erro, openai.RateLimitError):
        return "Limite de uso da OpenAI atingido (429). Tente de novo em instantes."
    return f"Erro na API da OpenAI ({erro.__class__.__name__}): {getattr(erro, 'message', erro)}"


def _executar(acao: Callable[[], object]):
    """Roda uma chamada ao agente; erros da API viram mensagem curta e saída com código 1."""
    try:
        return acao()
    except openai.APIError as erro:
        console.print(f"[red]{_mensagem_de_erro_da_api(erro)}[/red]")
        raise typer.Exit(code=1) from None


def _aviso_tracing() -> None:
    ativo = os.environ.get("LANGSMITH_TRACING", "").lower() == "true"
    if ativo and os.environ.get("LANGSMITH_API_KEY"):
        projeto = os.environ.get("LANGSMITH_PROJECT", "default")
        console.print(f"[dim]LangSmith: tracing ativo (projeto '{projeto}').[/dim]")
    else:
        console.print(
            "[dim]LangSmith: tracing desligado (defina LANGSMITH_TRACING e a chave).[/dim]"
        )


def _responder_com_streaming(agente, pergunta: str, thread_id: str) -> None:
    """Mostra a resposta token a token; ferramentas aparecem em linhas discretas."""
    config = {"configurable": {"thread_id": thread_id}}
    entrada = {"messages": [HumanMessage(content=validar_pergunta(pergunta))]}
    console.print("[bold green]Tutor:[/bold green] ", end="")
    for mensagem, _metadados in agente.stream(entrada, config, stream_mode="messages"):
        if isinstance(mensagem, ToolMessage):
            console.print(f"\n[dim]↳ ferramenta usada: {mensagem.name}[/dim]")
        elif isinstance(mensagem, AIMessageChunk) and mensagem.text:
            console.print(mensagem.text, end="", markup=False, highlight=False)
    console.print()


def main(
    pergunta: Annotated[
        str | None, typer.Option(help="Faz uma única pergunta e sai (sem modo interativo).")
    ] = None,
    rag: Annotated[bool, typer.Option(help="Usa a busca semântica da Questão 3.")] = False,
    tutor: Annotated[bool, typer.Option(help="Permite encaminhar para tutor humano.")] = True,
    streaming: Annotated[bool, typer.Option(help="Mostra a resposta token a token.")] = True,
    thread_id: Annotated[str | None, typer.Option(help="Reaproveita uma conversa.")] = None,
) -> None:
    """Chatbot sobre programação em Python (LangChain + OpenAI)."""
    if settings.openai_api_key is None:
        console.print("[red]OPENAI_API_KEY não configurada.[/red] Copie .env.example para .env.")
        raise typer.Exit(code=1)

    console.print(f"[dim]Modelo: {settings.openai_model}[/dim]")
    _aviso_tracing()
    try:
        agente = criar_agente(com_rag=rag, com_tutor=tutor)
    except FileNotFoundError as erro:  # índice da Q3 ausente com --rag
        console.print(f"[red]{erro}[/red]")
        raise typer.Exit(code=1) from erro

    thread_id = thread_id or str(uuid.uuid4())

    if pergunta is not None:
        resposta = _executar(lambda: perguntar(agente, pergunta, thread_id))
        console.print(Panel(Markdown(resposta.texto), title="Tutor", border_style="green"))
        console.print(
            f"[dim]tokens: {resposta.tokens_entrada} entrada + {resposta.tokens_saida} saída"
            f" | ferramentas: {', '.join(resposta.ferramentas_usadas) or 'nenhuma'}[/dim]"
        )
        return

    console.print(
        Panel(
            "Pergunte sobre Python. Comandos: [bold]/novo[/bold] zera o histórico, "
            "[bold]/sair[/bold] encerra.",
            title="Chatbot de Python",
        )
    )
    while True:
        try:
            texto = console.input("[bold cyan]Você:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nAté mais!")
            break
        if not texto:
            continue
        if texto.lower() in {"/sair", "sair", "exit", "quit"}:
            console.print("Até mais!")
            break
        if texto.lower() == "/novo":
            thread_id = str(uuid.uuid4())
            console.print("[dim]Nova conversa iniciada (histórico zerado).[/dim]")
            continue
        try:
            if streaming:
                _responder_com_streaming(agente, texto, thread_id)
            else:
                resposta = perguntar(agente, texto, thread_id)
                console.print(Panel(Markdown(resposta.texto), title="Tutor", border_style="green"))
        except ValueError as erro:  # pergunta vazia/longa
            console.print(f"[yellow]{erro}[/yellow]")
        except openai.AuthenticationError as erro:  # sem chave válida não adianta insistir
            console.print(f"[red]{_mensagem_de_erro_da_api(erro)}[/red]")
            raise typer.Exit(code=1) from None
        except openai.APIError as erro:  # erro transitório: avisa e segue a conversa
            console.print(f"[red]{_mensagem_de_erro_da_api(erro)}[/red]")


app.command()(main)

if __name__ == "__main__":
    app()
