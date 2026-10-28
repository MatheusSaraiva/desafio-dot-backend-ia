"""Busca híbrida: funde o ranking semântico (FAISS) e o lexical (BM25).

Os dois métodos erram de formas diferentes: o semântico confunde documentos vizinhos
(listas vs. list comprehension), o lexical falha quando a consulta não repete palavras
do documento. A fusão por Reciprocal Rank Fusion (RRF) combina os rankings sem precisar
calibrar as escalas de score, que são incomparáveis (cosseno vs. BM25):

    score(doc) = soma, para cada ranking, de 1 / (rrf_k + posição do doc no ranking)

É o mesmo princípio da busca híbrida do OpenSearch/Elasticsearch em produção.
"""

from dataclasses import replace

from .evaluate import BuscadorBM25
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

    def buscar(self, consulta: str, k: int = 5) -> list[ResultadoBusca]:
        candidatos = k * 4  # cada método contribui com um ranking mais longo que o final
        rankings = [
            self.semantico.buscar(consulta, k=candidatos),
            self.bm25.buscar(consulta, k=candidatos),
        ]
        pontuacao: dict[str, float] = {}
        melhor_resultado: dict[str, ResultadoBusca] = {}
        for ranking in rankings:
            for posicao, resultado in enumerate(ranking, start=1):
                pontuacao[resultado.doc_id] = pontuacao.get(resultado.doc_id, 0.0) + 1 / (
                    self.rrf_k + posicao
                )
                # Trecho exibido: o do primeiro ranking que trouxe o documento (semântico).
                melhor_resultado.setdefault(resultado.doc_id, resultado)

        ordenados = sorted(pontuacao, key=lambda doc_id: pontuacao[doc_id], reverse=True)[:k]
        return [
            replace(melhor_resultado[doc_id], score=round(pontuacao[doc_id], 4))
            for doc_id in ordenados
        ]
