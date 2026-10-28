"""Geração de embeddings.

Dois "embedders" com a mesma interface:
- `SentenceTransformerEmbedder`: modelo real da HuggingFace (sentence-transformers);
- `FakeEmbedder`: vetor determinístico baseado nas palavras, para testes rápidos e offline.

Os vetores são sempre normalizados (norma 1). Com isso, o produto interno que o FAISS
calcula (`IndexFlatIP`) é exatamente a similaridade de cosseno.
"""

import hashlib
import re
import unicodedata
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    nome: str
    dimensao: int

    def embed_passages(self, textos: list[str]) -> np.ndarray: ...

    def embed_queries(self, textos: list[str]) -> np.ndarray: ...


class SentenceTransformerEmbedder:
    """Embeddings com um modelo do sentence-transformers (carregado sob demanda)."""

    def __init__(self, nome_modelo: str, batch_size: int = 32) -> None:
        self.nome = nome_modelo
        self.batch_size = batch_size
        self._modelo = None
        # A família e5 foi treinada com prefixos que distinguem pergunta de documento;
        # sem eles a qualidade cai. Outros modelos não precisam.
        self._usa_prefixo_e5 = "e5" in nome_modelo.lower()

    @property
    def modelo(self):
        if self._modelo is None:
            # Import local: torch/transformers são pesados e só carregam quando necessário.
            from sentence_transformers import SentenceTransformer

            self._modelo = SentenceTransformer(self.nome)
        return self._modelo

    @property
    def dimensao(self) -> int:
        return int(self.modelo.get_sentence_embedding_dimension())

    def _encode(self, textos: list[str]) -> np.ndarray:
        vetores = self.modelo.encode(
            textos,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        # FAISS exige float32 contíguo.
        return np.ascontiguousarray(vetores, dtype=np.float32)

    def embed_passages(self, textos: list[str]) -> np.ndarray:
        if self._usa_prefixo_e5:
            textos = [f"passage: {t}" for t in textos]
        return self._encode(textos)

    def embed_queries(self, textos: list[str]) -> np.ndarray:
        if self._usa_prefixo_e5:
            textos = [f"query: {t}" for t in textos]
        return self._encode(textos)


def _normalizar_token(token: str) -> str:
    """Minúsculas, sem acentos e truncado: 'Listas' e 'lista' viram o mesmo 'lista'."""
    sem_acento = unicodedata.normalize("NFKD", token.lower()).encode("ascii", "ignore").decode()
    return sem_acento[:5]


class FakeEmbedder:
    """Embedding "bag of words" com hashing, para testes.

    Não entende semântica (sinônimos não se aproximam), mas é determinístico entre
    processos, não baixa nada e preserva a propriedade que importa para testar o
    pipeline: textos que compartilham palavras ficam próximos.
    """

    nome = "fake-hash-bow"

    def __init__(self, dimensao: int = 256) -> None:
        self.dimensao = dimensao

    def _vetor(self, texto: str) -> np.ndarray:
        vetor = np.zeros(self.dimensao, dtype=np.float32)
        for token in re.findall(r"\w+", texto):
            if len(token) < 3:
                continue  # ignora "de", "a", "em"...
            stem = _normalizar_token(token)
            # hashlib em vez de hash(): o hash() de str muda a cada processo do Python.
            posicao = int(hashlib.md5(stem.encode()).hexdigest(), 16) % self.dimensao
            vetor[posicao] += 1.0
        vetor = np.log1p(vetor)  # amortece palavras muito repetidas
        norma = np.linalg.norm(vetor)
        return vetor / norma if norma > 0 else vetor

    def embed_passages(self, textos: list[str]) -> np.ndarray:
        return np.vstack([self._vetor(t) for t in textos]).astype(np.float32)

    def embed_queries(self, textos: list[str]) -> np.ndarray:
        return self.embed_passages(textos)
