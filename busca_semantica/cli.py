"""Interface de linha de comando da busca semântica.

uv run python -m busca_semantica.cli build-index
uv run python -m busca_semantica.cli search "como percorrer uma lista" --k 3
uv run python -m busca_semantica.cli evaluate
"""

import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .config import settings
from .embeddings import SentenceTransformerEmbedder
from .evaluate import CONSULTAS_AVALIACAO, BuscadorBM25, avaliar
from .search import BuscadorSemantico, carregar_buscador, construir_indice

app = typer.Typer(help="Busca semântica de documentos com embeddings + FAISS (Questão 3).")
console = Console()

OpcaoIndice = Annotated[Path, typer.Option(help="Pasta onde o índice fica salvo.")]
OpcaoModelo = Annotated[str, typer.Option(help="Modelo de embeddings (HuggingFace).")]


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
    index_dir: OpcaoIndice = settings.index_dir,
    trecho: Annotated[bool, typer.Option(help="Mostrar o trecho que casou.")] = True,
) -> None:
    """Retorna os documentos mais relevantes para a consulta."""
    buscador = carregar_buscador(index_dir)
    inicio = time.perf_counter()
    resultados = buscador.buscar(consulta, k=k)
    duracao_ms = (time.perf_counter() - inicio) * 1000

    tabela = Table(title=f'Resultados para "{consulta}"', show_lines=trecho)
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
    """Mede recall@1, recall@k e MRR da busca semântica e compara com BM25 (lexical)."""
    semantico = carregar_buscador(index_dir)
    bm25 = BuscadorBM25(semantico.indice.chunks)

    resultados = {
        "Semântica (FAISS)": avaliar(semantico, CONSULTAS_AVALIACAO, k=k),
        "BM25 (lexical)": avaliar(bm25, CONSULTAS_AVALIACAO, k=k),
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
    detalhe.add_column("Semântica", justify="center")
    detalhe.add_column("BM25", justify="center")
    sem_det = resultados["Semântica (FAISS)"].detalhes
    bm_det = resultados["BM25 (lexical)"].detalhes
    for s, b in zip(sem_det, bm_det, strict=True):
        detalhe.add_row(
            s.consulta,
            s.esperado,
            str(s.posicao) if s.posicao else "[red]-[/red]",
            str(b.posicao) if b.posicao else "[red]-[/red]",
        )
    console.print(detalhe)


def _buscador_para_teste_rapido() -> BuscadorSemantico:  # pragma: no cover
    """Atalho usado em exploração manual (python -c)."""
    return carregar_buscador()


if __name__ == "__main__":
    app()
