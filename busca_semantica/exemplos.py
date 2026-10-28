"""Gera o arquivo de exemplos da busca semântica, em Markdown.

    uv run python -m busca_semantica.exemplos > docs/exemplos_q3.md

Usa o índice salvo em disco (rode `make build-index` antes). Carrega o modelo uma única
vez e imprime: consultas de exemplo com os 3 melhores documentos, e a avaliação
recall@k / MRR comparada com o baseline BM25.
"""

from datetime import date

from .evaluate import CONSULTAS_AVALIACAO, BuscadorBM25, avaliar
from .hybrid import BuscadorHibrido
from .search import carregar_buscador

# Consultas escolhidas para mostrar semântica (paráfrases, sinônimos, dois domínios).
CONSULTAS_EXEMPLO = [
    "como criar uma lista e adicionar itens",
    "percorrer os elementos de uma coleção",
    "o que acontece quando o programa encontra um erro",
    "isolar as dependências de cada projeto",
    "economizar memória ao processar um arquivo gigante",
    "como funciona um tutor de IA que responde com base no material do curso",
    "quando o robô deve chamar um humano",
    "proteção de dados pessoais na plataforma de ensino",
]


def _resumo(texto: str, limite: int = 220) -> str:
    texto = " ".join(texto.split())
    return texto if len(texto) <= limite else texto[:limite].rsplit(" ", 1)[0] + "…"


def main() -> None:
    buscador = carregar_buscador()
    indice = buscador.indice
    print("# Exemplos de busca semântica (Questão 3)\n")
    print(
        f"Gerado em {date.today().isoformat()} com `uv run python -m busca_semantica.exemplos`. "
        f"Modelo `{indice.nome_modelo}` (dimensão {indice.dimensao}), "
        f"{len(indice)} chunks de {len({c.doc_id for c in indice.chunks})} documentos.\n"
    )

    print("## Consultas de exemplo (top 3 por documento)\n")
    for consulta in CONSULTAS_EXEMPLO:
        print(f"### “{consulta}”\n")
        print("| # | Score | Documento | Trecho que casou |")
        print("|---|---|---|---|")
        for pos, r in enumerate(buscador.buscar(consulta, k=3), start=1):
            print(f"| {pos} | {r.score:.3f} | {r.titulo} (`{r.doc_id}`) | {_resumo(r.trecho)} |")
        print()

    k = 3
    bm25 = BuscadorBM25(indice.chunks)
    metodos = {
        "Semântica (e5 + FAISS)": avaliar(buscador, CONSULTAS_AVALIACAO, k=k),
        "BM25 (lexical)": avaliar(bm25, CONSULTAS_AVALIACAO, k=k),
        "Híbrida (RRF)": avaliar(BuscadorHibrido(buscador, bm25), CONSULTAS_AVALIACAO, k=k),
    }

    print(f"## Avaliação: {len(CONSULTAS_AVALIACAO)} consultas com resposta conhecida (k={k})\n")
    print(
        "As consultas foram escritas como paráfrases, com pouca sobreposição de palavras "
        "com os documentos, para medir compreensão de significado e não casamento de termos.\n"
    )
    print(f"| Método | recall@1 | recall@{k} | MRR@{k} |")
    print("|---|---|---|---|")
    for nome, m in metodos.items():
        print(f"| {nome} | {m.recall_at_1:.2f} | {m.recall_at_k:.2f} | {m.mrr:.3f} |")
    print()

    print("| Consulta | Documento esperado | Semântica | BM25 | Híbrida |")
    print("|---|---|---|---|---|")
    detalhes = zip(*(m.detalhes for m in metodos.values()), strict=True)
    for s, b, h in detalhes:
        posicoes = [str(d.posicao) if d.posicao else f"fora do top {k}" for d in (s, b, h)]
        print(f"| {s.consulta} | `{s.esperado}` | " + " | ".join(posicoes) + " |")


if __name__ == "__main__":
    main()
