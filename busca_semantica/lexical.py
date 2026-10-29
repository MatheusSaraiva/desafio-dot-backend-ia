"""Busca lexical (BM25) sobre os mesmos chunks do índice vetorial.

Tem dois papéis: baseline na avaliação (mostra onde a busca semântica ganha) e segunda
perna da busca híbrida, porque acha o que a semântica perde quando a consulta repete
termos exatos do documento (nomes de função, siglas, mensagens de erro).
"""

import re
import unicodedata

from rank_bm25 import BM25Okapi

from .ingest import Chunk
from .search import ResultadoBusca

_STOPWORDS = frozenset(
    "a o e de da do das dos em um uma uns umas para por com sem que se na no nas nos ao aos "
    "as os ou mas como mais muito ja nao sim seu sua seus suas ele ela eles elas voce isso "
    "isto esse essa este esta pelo pela ate entre sobre quando onde qual quais ser ter foi "
    "sao era sera pode podem tambem".split()
)


def tokenizar(texto: str) -> list[str]:
    """Minúsculas, sem acentos, só palavras, sem stopwords. Tokenizador simples de propósito."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [t for t in re.findall(r"\w+", sem_acento) if t not in _STOPWORDS and len(t) > 1]


class BuscadorBM25:
    """Busca lexical com a mesma interface do buscador semântico (`Buscador`)."""

    nome = "bm25"

    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenizar(c.texto_para_embedding) for c in chunks])

    def buscar(
        self, consulta: str, k: int = 5, agrupar_por_documento: bool = True
    ) -> list[ResultadoBusca]:
        scores = self.bm25.get_scores(tokenizar(consulta))
        ordem = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)
        resultados: list[ResultadoBusca] = []
        vistos: set[str] = set()
        for i in ordem:
            if scores[i] <= 0:
                # Nenhum termo em comum com a consulta: não é um resultado, é ruído.
                # Devolvê-lo poluiria a fusão com a busca semântica (RRF).
                break
            chunk = self.chunks[i]
            if agrupar_por_documento:
                if chunk.doc_id in vistos:
                    continue
                vistos.add(chunk.doc_id)
            resultados.append(
                ResultadoBusca(
                    doc_id=chunk.doc_id,
                    titulo=chunk.titulo,
                    fonte=chunk.fonte,
                    score=round(float(scores[i]), 4),
                    trecho=chunk.texto,
                    indice_chunk=chunk.indice,
                )
            )
            if len(resultados) == k:
                break
        return resultados
