"""Vector store com FAISS.

Usa `IndexFlatIP` (produto interno, busca exata). Para um corpus de dezenas ou milhares
de chunks é a escolha certa: sem treino, sem aproximação, resultado exato. Com milhões
de vetores trocaríamos por um índice aproximado (IVF ou HNSW) ou por um serviço
(Milvus, OpenSearch k-NN), mantendo esta mesma interface.
"""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import faiss
import numpy as np

from .ingest import Chunk

ARQUIVO_INDICE = "index.faiss"
ARQUIVO_CHUNKS = "chunks.jsonl"
ARQUIVO_META = "meta.json"


class IndiceVetorial:
    def __init__(self, dimensao: int, nome_modelo: str) -> None:
        self.dimensao = dimensao
        self.nome_modelo = nome_modelo
        self.index = faiss.IndexFlatIP(dimensao)
        # Posição i do FAISS <-> chunks[i]. O FAISS guarda só vetores; o texto fica aqui.
        self.chunks: list[Chunk] = []

    def __len__(self) -> int:
        return self.index.ntotal

    def adicionar(self, vetores: np.ndarray, chunks: list[Chunk]) -> None:
        if len(vetores) != len(chunks):
            raise ValueError("Quantidade de vetores e de chunks precisa ser igual.")
        if vetores.shape[1] != self.dimensao:
            raise ValueError(f"Vetores com dimensão {vetores.shape[1]}, esperado {self.dimensao}.")
        self.index.add(np.ascontiguousarray(vetores, dtype=np.float32))
        self.chunks.extend(chunks)

    def buscar(self, vetor_consulta: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        """Retorna os k chunks mais parecidos com o vetor, do mais ao menos parecido."""
        if len(self) == 0:
            return []
        k = min(k, len(self))
        consulta = np.ascontiguousarray(vetor_consulta.reshape(1, -1), dtype=np.float32)
        scores, posicoes = self.index.search(consulta, k)
        return [
            (self.chunks[pos], float(score))
            for pos, score in zip(posicoes[0], scores[0], strict=True)
            if pos >= 0  # o FAISS devolve -1 quando não há vizinhos suficientes
        ]

    def salvar(self, pasta: Path) -> None:
        """Persiste índice + chunks + metadados; permite reutilizar sem reprocessar."""
        pasta.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(pasta / ARQUIVO_INDICE))
        with (pasta / ARQUIVO_CHUNKS).open("w", encoding="utf-8") as arquivo:
            for chunk in self.chunks:
                arquivo.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
        meta = {
            "modelo": self.nome_modelo,
            "dimensao": self.dimensao,
            "total_chunks": len(self),
            "criado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        (pasta / ARQUIVO_META).write_text(json.dumps(meta, indent=2), encoding="utf-8")

    @classmethod
    def carregar(cls, pasta: Path) -> "IndiceVetorial":
        meta = json.loads((pasta / ARQUIVO_META).read_text(encoding="utf-8"))
        indice = cls(dimensao=meta["dimensao"], nome_modelo=meta["modelo"])
        indice.index = faiss.read_index(str(pasta / ARQUIVO_INDICE))
        with (pasta / ARQUIVO_CHUNKS).open(encoding="utf-8") as arquivo:
            indice.chunks = [Chunk(**json.loads(linha)) for linha in arquivo if linha.strip()]
        if len(indice.chunks) != indice.index.ntotal:
            raise ValueError("Índice corrompido: número de chunks difere do número de vetores.")
        return indice
