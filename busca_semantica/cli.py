"""Interface de linha de comando da busca semântica.

uv run python -m busca_semantica.cli build-index
uv run python -m busca_semantica.cli search "como percorrer uma lista" --k 3
uv run python -m busca_semantica.cli search "..." --modo hibrida --por-chunk
uv run python -m busca_semantica.cli search "receita de bolo" --score-minimo 0.83
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
from .evaluate import CONSULTAS_AVALIACAO, avaliar, calibrar_score_minimo
from .hybrid import BuscadorHibrido
from .lexical import BuscadorBM25
from .search import Buscador, carregar_buscador, construir_indice

app = typer.Typer(
    help="Busca semântica de documentos com embeddings + FAISS (Questão 3).",
    pretty_exceptions_show_locals=False,
)
console = Console()


class Modo(StrEnum):
    semantica = "semantica"
    bm25 = "bm25"
    hibrida = "hibrida"


# O que a coluna "score" significa em cada modo (as escalas não são comparáveis).
ROTULO_SCORE = {Modo.semantica: "Cosseno", Modo.bm25: "BM25", Modo.hibrida: "RRF"}

OpcaoIndice = Annotated[Path, typer.Option(help="Pasta onde o índice fica salvo.")]
OpcaoModelo = Annotated[str, typer.Option(help="Modelo de embeddings (HuggingFace).")]


def _buscadores(index_dir: Path, score_minimo: float | None = None) -> dict[Modo, Buscador]:
    semantico = carregar_buscador(index_dir, score_minimo=score_minimo)
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
    # O modelo trunca em silêncio o que passa do limite: melhor saber agora que na busca.
    maior = max(embedder.contar_tokens(c.texto_para_embedding) for c in indice.chunks)
    limite = embedder.limite_tokens
    if maior > limite:
        console.print(
            f"[red]Atenção: o maior chunk tem {maior} tokens e o modelo lê {limite}; "
            f"o excedente é ignorado. Reduza chunk_size em config.py.[/red]"
        )
    else:
        console.print(f"[dim]Maior chunk: {maior} tokens (limite do modelo: {limite}).[/dim]")


@app.command()
def search(
    consulta: Annotated[str, typer.Argument(help="Texto da consulta, em linguagem natural.")],
    k: Annotated[int, typer.Option(help="Quantos resultados retornar.")] = 5,
    modo: Annotated[
        Modo, typer.Option(help="semantica (FAISS), bm25 ou hibrida.")
    ] = Modo.semantica,
    por_chunk: Annotated[
        bool, typer.Option(help="Lista chunks em vez de documentos (como o RAG do chatbot vê).")
    ] = False,
    score_minimo: Annotated[
        float | None,
        typer.Option(
            help=f"Cosseno mínimo para devolver um resultado (o RAG usa {settings.score_minimo})."
        ),
    ] = None,
    index_dir: OpcaoIndice = settings.index_dir,
    trecho: Annotated[bool, typer.Option(help="Mostrar o trecho que casou.")] = True,
) -> None:
    """Retorna os documentos (ou chunks) mais relevantes para a consulta."""
    buscador = _buscadores(index_dir, score_minimo)[modo]
    inicio = time.perf_counter()
    resultados = buscador.buscar(consulta, k=k, agrupar_por_documento=not por_chunk)
    duracao_ms = (time.perf_counter() - inicio) * 1000

    tabela = Table(title=f'Resultados para "{consulta}" (modo {modo.value})', show_lines=trecho)
    tabela.add_column("#", justify="right")
    tabela.add_column(ROTULO_SCORE[modo], justify="right")
    tabela.add_column("Documento")
    if trecho:
        tabela.add_column("Trecho", overflow="fold")
    for posicao, r in enumerate(resultados, start=1):
        documento = f"{r.titulo}\n[dim]{r.doc_id}" + (f" #{r.indice_chunk}" if por_chunk else "")
        linha = [str(posicao), f"{r.score:.3f}", documento + "[/dim]"]
        if trecho:
            linha.append(r.trecho[:300] + ("..." if len(r.trecho) > 300 else ""))
        tabela.add_row(*linha)
    console.print(tabela)
    if not resultados and score_minimo is not None:
        console.print(
            f"[yellow]Nenhum trecho com cosseno >= {score_minimo}: fora do domínio.[/yellow]"
        )
    console.print(f"[dim]{len(resultados)} resultado(s) em {duracao_ms:.0f} ms[/dim]")


@app.command()
def evaluate(
    index_dir: OpcaoIndice = settings.index_dir,
    k: Annotated[int, typer.Option(help="Profundidade do ranking avaliado.")] = 3,
) -> None:
    """Mede recall@1, recall@k e MRR das buscas, e confere o limiar de relevância."""
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

    calibracao = calibrar_score_minimo(
        buscadores[Modo.semantica], score_minimo=settings.score_minimo
    )
    limiar = Table(title="Limiar de relevância (cosseno do 1º resultado)")
    limiar.add_column("Grupo")
    limiar.add_column("Consulta", overflow="fold")
    limiar.add_column("Cosseno", justify="right")
    pior_no_dominio = min(calibracao.no_dominio, key=lambda item: item[1])
    limiar.add_row(
        "com resposta na base (pior caso)", pior_no_dominio[0], f"{pior_no_dominio[1]:.3f}"
    )
    for consulta, score in calibracao.fora_do_dominio:
        limiar.add_row("fora do domínio", consulta, f"{score:.3f}")
    console.print(limiar)
    veredito = "separa os dois grupos" if calibracao.separa else "NÃO separa os dois grupos"
    console.print(
        f"score_minimo configurado = {settings.score_minimo}: {veredito} "
        f"(domínio >= {calibracao.menor_no_dominio:.3f}, fora <= "
        f"{calibracao.maior_fora_do_dominio:.3f}; ponto médio {calibracao.sugestao})."
    )


if __name__ == "__main__":
    app()
