"""Busca híbrida: funde o ranking semântico (FAISS) e o lexical (BM25).

Os dois métodos erram de formas diferentes: o semântico confunde documentos vizinhos
(listas vs. list comprehension), o lexical falha quando a consulta não repete palavras
do documento. A fusão por Reciprocal Rank Fusion (RRF) combina os rankings sem precisar
calibrar as escalas de score, que são incomparáveis (cosseno vs. BM25):

    score(item) = soma, para cada ranking, de 1 / (rrf_k + posição do item no ranking)

É o mesmo princípio da busca híbrida do OpenSearch/Elasticsearch em produção.
"""

from collections.abc import Callable
from dataclasses import replace

from .lexical import BuscadorBM25
from .search import BuscadorSemantico, ResultadoBusca


class BuscadorHibrido:
    nome = "hibrida"

    def __init__(
        self,
        semantico: BuscadorSemantico,
        bm25: BuscadorBM25 | None = None,
        rrf_k: int = 60,
    ) -> None:
        self.semantico = semantico
        # O BM25 é construído sobre os mesmos chunks do índice vetorial.
        self.bm25 = bm25 or BuscadorBM25(semantico.indice.chunks)
        self.rrf_k = rrf_k  # 60 é o valor clássico do artigo original do RRF

    def buscar(
        self, consulta: str, k: int = 5, agrupar_por_documento: bool = True
    ) -> list[ResultadoBusca]:
        """Funde os dois rankings. Agrupando, o item fundido é o documento; sem agrupar, o chunk.

        O score devolvido é o do RRF (soma de 1/(k+posição)); serve para ordenar, não é uma
        similaridade. O filtro de relevância é o do buscador semântico (`score_minimo`):
        se nenhum chunk passa nele, a consulta está fora do domínio da base e a resposta é
        vazia, mesmo que o BM25 tenha algum termo em comum.
        """
        candidatos = k * 4  # cada método contribui com um ranking mais longo que o final
        ranking_semantico = self.semantico.buscar(consulta, candidatos, agrupar_por_documento)
        if not ranking_semantico:
            return []
        ranking_bm25 = self.bm25.buscar(consulta, candidatos, agrupar_por_documento)

        chave: Callable[[ResultadoBusca], object] = (
            (lambda r: r.doc_id)
            if agrupar_por_documento
            else (lambda r: (r.doc_id, r.indice_chunk))
        )
        pontuacao: dict[object, float] = {}
        primeiro_resultado: dict[object, ResultadoBusca] = {}
        for ranking in (ranking_semantico, ranking_bm25):
            for posicao, resultado in enumerate(ranking, start=1):
                item = chave(resultado)
                pontuacao[item] = pontuacao.get(item, 0.0) + 1 / (self.rrf_k + posicao)
                # Trecho exibido: o do primeiro ranking que trouxe o item (o semântico).
                primeiro_resultado.setdefault(item, resultado)

        ordenados = sorted(pontuacao, key=lambda item: pontuacao[item], reverse=True)[:k]
        return [
            replace(primeiro_resultado[item], score=round(pontuacao[item], 4)) for item in ordenados
        ]
