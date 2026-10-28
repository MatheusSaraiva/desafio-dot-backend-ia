"""Interface de linha de comando da busca semântica.

uv run python -m busca_semantica.cli build-index
uv run python -m busca_semantica.cli search "como percorrer uma lista" --k 3
uv run python -m busca_semantica.cli search "..." --modo hibrida
uv run python -m busca_semantica.cli evaluate
"""

import time
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .config import settings
from .embeddings import SentenceTransformerEmbedder
from .evaluate import CONSULTAS_AVALIACAO, BuscadorBM25, avaliar
from .hybrid import BuscadorHibrido
from .search import carregar_buscador, construir_indice

app = typer.Typer(
    help="Busca semântica de documentos com embeddings + FAISS (Questão 3).",
    pretty_exceptions_show_locals=False,
)
console = Console()


class Modo(StrEnum):
    semantica = "semantica"
    bm25 = "bm25"
    hibrida = "hibrida"


OpcaoIndice = Annotated[Path, typer.Option(help="Pasta onde o índice fica salvo.")]
OpcaoModelo = Annotated[str, typer.Option(help="Modelo de embeddings (HuggingFace).")]


def _buscadores(index_dir: Path) -> dict[Modo, object]:
    semantico = carregar_buscador(index_dir)
    # Carrega o modelo agora (uma vez) para que o tempo medido na busca seja só da busca.
    getattr(semantico.embedder, "modelo", None)
    bm25 = BuscadorBM25(semantico.indice.chunks)
    return {
        Modo.semantica: semantico,
        Modo.bm25: bm25,
        Modo.hibrida: BuscadorHibrido(semantico, bm25),
    }


@app.command("build-index")
def build_index(
    corpus: Annotated[Path, typer.Option(help="Pasta com os .md do corpus.")] = settings.corpus_dir,
    index_dir: OpcaoIndice = settings.index_dir,
    model: OpcaoModelo = settings.embedding_model,
) -> None:
    """Lê o corpus, gera os embeddings e salva o índice FAISS em disco."""
    inicio = time.perf_counter()
    embedder = SentenceTransformerEmbedder(model)
    console.print(f"Modelo: [bold]{model}[/bold] (carregando...)")
    indice = construir_indice(corpus, embedder)
    indice.salvar(index_dir)
    console.print(
        f"Índice salvo em [bold]{index_dir}[/bold]: {len(indice)} chunks, "
        f"dimensão {indice.dimensao}, {time.perf_counter() - inicio:.1f}s."
    )


@app.command()
def search(
    consulta: Annotated[str, typer.Argument(help="Texto da consulta, em linguagem natural.")],
    k: Annotated[int, typer.Option(help="Quantos documentos retornar.")] = 5,
    modo: Annotated[
        Modo, typer.Option(help="semantica (FAISS), bm25 ou hibrida.")
    ] = Modo.semantica,
    index_dir: OpcaoIndice = settings.index_dir,
    trecho: Annotated[bool, typer.Option(help="Mostrar o trecho que casou.")] = True,
) -> None:
    """Retorna os documentos mais relevantes para a consulta."""
    buscador = _buscadores(index_dir)[modo]
    inicio = time.perf_counter()
    resultados = buscador.buscar(consulta, k=k)
    duracao_ms = (time.perf_counter() - inicio) * 1000

    tabela = Table(title=f'Resultados para "{consulta}" (modo {modo.value})', show_lines=trecho)
    tabela.add_column("#", justify="right")
    tabela.add_column("Score", justify="right")
    tabela.add_column("Documento")
    if trecho:
        tabela.add_column("Trecho", overflow="fold")
    for posicao, r in enumerate(resultados, start=1):
        linha = [str(posicao), f"{r.score:.3f}", f"{r.titulo}\n[dim]{r.doc_id}[/dim]"]
        if trecho:
            linha.append(r.trecho[:300] + ("..." if len(r.trecho) > 300 else ""))
        tabela.add_row(*linha)
    console.print(tabela)
    console.print(f"[dim]{len(resultados)} resultado(s) em {duracao_ms:.0f} ms[/dim]")


@app.command()
def evaluate(
    index_dir: OpcaoIndice = settings.index_dir,
    k: Annotated[int, typer.Option(help="Profundidade do ranking avaliado.")] = 3,
) -> None:
    """Mede recall@1, recall@k e MRR das buscas semântica, BM25 e híbrida."""
    buscadores = _buscadores(index_dir)
    resultados = {
        modo.value: avaliar(buscador, CONSULTAS_AVALIACAO, k=k)
        for modo, buscador in buscadores.items()
    }

    resumo = Table(title=f"{len(CONSULTAS_AVALIACAO)} consultas, k={k}")
    resumo.add_column("Método")
    resumo.add_column("recall@1", justify="right")
    resumo.add_column(f"recall@{k}", justify="right")
    resumo.add_column(f"MRR@{k}", justify="right")
    for nome, m in resultados.items():
        resumo.add_row(nome, f"{m.recall_at_1:.2f}", f"{m.recall_at_k:.2f}", f"{m.mrr:.3f}")
    console.print(resumo)

    detalhe = Table(title="Posição do documento esperado em cada consulta")
    detalhe.add_column("Consulta", overflow="fold")
    detalhe.add_column("Esperado")
    for nome in resultados:
        detalhe.add_column(nome, justify="center")
    for linhas in zip(*(m.detalhes for m in resultados.values()), strict=True):
        posicoes = [str(d.posicao) if d.posicao else "[red]-[/red]" for d in linhas]
        detalhe.add_row(linhas[0].consulta, linhas[0].esperado, *posicoes)
    console.print(detalhe)


if __name__ == "__main__":
    app()
