"""Testes da Questão 3 (busca semântica).

Os testes rápidos usam o `FakeEmbedder` (sem download, determinístico) e cobrem todo o
pipeline: corpus -> chunks -> índice FAISS -> busca -> persistência -> avaliação.
O teste marcado `slow` usa o modelo real e valida a semântica de verdade.
"""

import numpy as np
import pytest

from busca_semantica.config import settings
from busca_semantica.embeddings import FakeEmbedder, SentenceTransformerEmbedder
from busca_semantica.evaluate import CONSULTAS_AVALIACAO, BuscadorBM25, avaliar
from busca_semantica.ingest import carregar_corpus, dividir_em_chunks
from busca_semantica.search import BuscadorSemantico, carregar_buscador, construir_indice


@pytest.fixture(scope="module")
def corpus():
    return carregar_corpus(settings.corpus_dir)


@pytest.fixture(scope="module")
def buscador_fake():
    embedder = FakeEmbedder()
    return BuscadorSemantico(construir_indice(settings.corpus_dir, embedder), embedder)


# ---------------------------------------------------------------- ingestão


def test_corpus_tem_documentos_com_metadados(corpus):
    assert len(corpus) >= 20
    ids = [d.doc_id for d in corpus]
    assert len(ids) == len(set(ids)), "doc_id precisa ser único"
    assert all(d.titulo and d.texto for d in corpus)


def test_consultas_de_avaliacao_apontam_para_documentos_existentes(corpus):
    ids = {d.doc_id for d in corpus}
    faltando = {esperado for _, esperado in CONSULTAS_AVALIACAO} - ids
    assert not faltando


def test_chunking_respeita_tamanho_e_preserva_origem(corpus):
    chunks = dividir_em_chunks(corpus, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > len(corpus)
    ids = {d.doc_id for d in corpus}
    assert all(c.doc_id in ids and c.texto for c in chunks)
    assert max(len(c.texto) for c in chunks) <= 500
    assert chunks[0].titulo in chunks[0].texto_para_embedding


# ---------------------------------------------------------------- embeddings


def test_fake_embedder_e_deterministico_e_normalizado():
    a = FakeEmbedder().embed_queries(["Listas em Python"])[0]
    b = FakeEmbedder().embed_queries(["listas em python"])[0]

    assert np.allclose(a, b)
    assert np.isclose(np.linalg.norm(a), 1.0)


def test_embedder_e5_adiciona_prefixos(monkeypatch):
    embedder = SentenceTransformerEmbedder("intfloat/multilingual-e5-small")
    recebidos: list[list[str]] = []
    monkeypatch.setattr(embedder, "_encode", lambda textos: recebidos.append(textos))

    embedder.embed_queries(["pergunta"])
    embedder.embed_passages(["documento"])

    assert recebidos == [["query: pergunta"], ["passage: documento"]]


# ---------------------------------------------------------------- busca


def test_busca_encontra_documento_com_os_termos_da_consulta(buscador_fake):
    resultados = buscador_fake.buscar("criar uma lista e adicionar itens com append", k=3)

    assert resultados[0].doc_id == "listas"
    assert resultados[0].score > 0
    assert resultados[0].trecho


def test_busca_agrupa_por_documento_e_respeita_k(buscador_fake):
    resultados = buscador_fake.buscar("python", k=4)

    ids = [r.doc_id for r in resultados]
    assert len(ids) == 4
    assert len(ids) == len(set(ids))


def test_busca_sem_agrupar_pode_repetir_documento(buscador_fake):
    resultados = buscador_fake.buscar("lista lista lista append", k=6, agrupar_por_documento=False)

    assert len(resultados) == 6


def test_busca_vazia_retorna_lista_vazia(buscador_fake):
    assert buscador_fake.buscar("   ") == []


def test_resultados_vem_em_ordem_decrescente_de_score(buscador_fake):
    scores = [r.score for r in buscador_fake.buscar("funções e parâmetros", k=5)]

    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------- persistência


def test_indice_salva_e_carrega_igual(tmp_path, buscador_fake):
    buscador_fake.indice.salvar(tmp_path)

    carregado = carregar_buscador(tmp_path, FakeEmbedder())

    assert len(carregado.indice) == len(buscador_fake.indice)
    consulta = "tratar erros com try e except"
    assert carregado.buscar(consulta, k=1) == buscador_fake.buscar(consulta, k=1)


def test_carregar_indice_com_modelo_diferente_falha(tmp_path, buscador_fake):
    buscador_fake.indice.salvar(tmp_path)
    outro = FakeEmbedder()
    outro.nome = "outro-modelo"

    with pytest.raises(ValueError, match="Reconstrua o índice"):
        carregar_buscador(tmp_path, outro)


def test_carregar_indice_inexistente_da_erro_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="build-index"):
        carregar_buscador(tmp_path / "nada", FakeEmbedder())


# ---------------------------------------------------------------- avaliação


def test_avaliacao_calcula_metricas(buscador_fake):
    consultas = [
        ("criar uma lista e adicionar itens com append", "listas"),
        ("xyzzy plugh termo inexistente", "listas"),
    ]

    metricas = avaliar(buscador_fake, consultas, k=3)

    assert metricas.k == 3
    assert len(metricas.detalhes) == 2
    assert metricas.detalhes[0].posicao == 1
    assert metricas.recall_at_1 == 0.5
    assert 0 <= metricas.mrr <= 1


def test_bm25_baseline_encontra_documento_por_palavras(corpus):
    chunks = dividir_em_chunks(corpus, settings.chunk_size, settings.chunk_overlap)
    bm25 = BuscadorBM25(chunks)

    resultados = bm25.buscar("list comprehension", k=3)

    assert resultados[0].doc_id == "list-comprehension"


# ---------------------------------------------------------------- modelo real


@pytest.mark.slow
def test_modelo_real_entende_parafrase():
    """Consulta sem nenhuma palavra do título: só um modelo semântico acerta."""
    embedder = SentenceTransformerEmbedder(settings.embedding_model)
    buscador = BuscadorSemantico(construir_indice(settings.corpus_dir, embedder), embedder)

    resultados = buscador.buscar("repetir um bloco de código para cada elemento", k=3)

    assert "loops-for-while" in [r.doc_id for r in resultados]
