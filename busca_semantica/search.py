"""Função de busca semântica: texto de consulta -> documentos mais relevantes."""

from dataclasses import dataclass
from pathlib import Path

from .config import settings
from .embeddings import Embedder, SentenceTransformerEmbedder
from .ingest import carregar_corpus, dividir_em_chunks
from .store import IndiceVetorial


@dataclass(frozen=True)
class ResultadoBusca:
    doc_id: str
    titulo: str
    fonte: str
    score: float  # similaridade de cosseno (quanto maior, mais parecido)
    trecho: str  # chunk que melhor casou com a consulta
    indice_chunk: int


class BuscadorSemantico:
    def __init__(self, indice: IndiceVetorial, embedder: Embedder) -> None:
        if indice.nome_modelo != embedder.nome:
            # Vetores de modelos diferentes vivem em espaços diferentes: comparar seria lixo.
            raise ValueError(
                f"Índice gerado com '{indice.nome_modelo}', mas o embedder é '{embedder.nome}'. "
                "Reconstrua o índice (build-index) com o mesmo modelo."
            )
        self.indice = indice
        self.embedder = embedder

    def buscar(
        self, consulta: str, k: int = 5, agrupar_por_documento: bool = True
    ) -> list[ResultadoBusca]:
        """Dado um texto, retorna os `k` resultados mais relevantes por similaridade semântica.

        Com `agrupar_por_documento` (padrão), cada documento aparece uma vez, representado
        pelo seu melhor chunk. Como vários chunks do mesmo documento podem estar no topo,
        pedimos mais candidatos ao FAISS antes de agrupar.
        """
        consulta = consulta.strip()
        if not consulta:
            return []
        vetor = self.embedder.embed_queries([consulta])[0]
        candidatos = self.indice.buscar(vetor, k=k * 4 if agrupar_por_documento else k)

        resultados: list[ResultadoBusca] = []
        vistos: set[str] = set()
        for chunk, score in candidatos:  # já vem ordenado por score decrescente
            if agrupar_por_documento and chunk.doc_id in vistos:
                continue
            vistos.add(chunk.doc_id)
            resultados.append(
                ResultadoBusca(
                    doc_id=chunk.doc_id,
                    titulo=chunk.titulo,
                    fonte=chunk.fonte,
                    score=round(score, 4),
                    trecho=chunk.texto,
                    indice_chunk=chunk.indice,
                )
            )
            if len(resultados) == k:
                break
        return resultados


def construir_indice(
    corpus_dir: Path,
    embedder: Embedder,
    chunk_size: int = settings.chunk_size,
    chunk_overlap: int = settings.chunk_overlap,
) -> IndiceVetorial:
    """Pipeline completo de indexação: ler -> dividir -> vetorizar -> indexar."""
    documentos = carregar_corpus(corpus_dir)
    chunks = dividir_em_chunks(documentos, chunk_size, chunk_overlap)
    vetores = embedder.embed_passages([c.texto_para_embedding for c in chunks])
    indice = IndiceVetorial(dimensao=vetores.shape[1], nome_modelo=embedder.nome)
    indice.adicionar(vetores, chunks)
    return indice


def embedder_padrao() -> Embedder:
    return SentenceTransformerEmbedder(settings.embedding_model)


def carregar_buscador(
    index_dir: Path = settings.index_dir, embedder: Embedder | None = None
) -> BuscadorSemantico:
    """Abre um índice salvo em disco e devolve um buscador pronto para uso."""
    if not (index_dir / "meta.json").exists():
        raise FileNotFoundError(
            f"Índice não encontrado em {index_dir}. Rode `make build-index` primeiro."
        )
    indice = IndiceVetorial.carregar(index_dir)
    return BuscadorSemantico(indice, embedder or embedder_padrao())
