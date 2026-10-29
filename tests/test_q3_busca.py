"""Testes da Questão 3 (busca semântica).

Os testes rápidos usam o `FakeEmbedder` (sem download, determinístico) e cobrem todo o
pipeline: corpus -> chunks -> índice FAISS -> busca -> persistência -> avaliação.
O teste marcado `slow` usa o modelo real e valida a semântica de verdade.
"""

import numpy as np
import pytest

from busca_semantica.config import settings
from busca_semantica.embeddings import FakeEmbedder, SentenceTransformerEmbedder
from busca_semantica.evaluate import CONSULTAS_AVALIACAO, avaliar, calibrar_score_minimo
from busca_semantica.hybrid import BuscadorHibrido
from busca_semantica.ingest import carregar_corpus, dividir_em_chunks
from busca_semantica.lexical import BuscadorBM25
from busca_semantica.search import BuscadorSemantico, carregar_buscador, construir_indice

# Consulta "fácil" para o embedder simulado (bag of words): só termos do artigo de listas.
CONSULTA_LISTAS = "lista append extend insert"


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
    resultados = buscador_fake.buscar(CONSULTA_LISTAS, k=3)

    assert resultados[0].doc_id == "listas"
    assert resultados[0].score > 0
    assert resultados[0].trecho


def test_busca_agrupa_por_documento_e_respeita_k(buscador_fake):
    resultados = buscador_fake.buscar("python", k=4)

    ids = [r.doc_id for r in resultados]
    assert len(ids) == 4
    assert len(ids) == len(set(ids))


def test_busca_sem_agrupar_devolve_chunks_e_pode_repetir_documento(buscador_fake):
    resultados = buscador_fake.buscar(
        "lista append extend insert remove pop sort", k=6, agrupar_por_documento=False
    )

    chaves = [(r.doc_id, r.indice_chunk) for r in resultados]
    assert len(chaves) == len(set(chaves)) == 6
    # O artigo de listas tem mais de um chunk e os dois falam de append/remove/sort.
    assert sum(1 for doc_id, _ in chaves if doc_id == "listas") >= 2


def test_busca_vazia_retorna_lista_vazia(buscador_fake):
    assert buscador_fake.buscar("   ") == []


def test_score_minimo_filtra_resultados_fracos(buscador_fake):
    sem_limiar = buscador_fake.buscar(CONSULTA_LISTAS, k=5)
    # Limiar entre o 1º e o 2º resultado: só o primeiro deve sobrar.
    corte = (sem_limiar[0].score + sem_limiar[1].score) / 2
    com_limiar = BuscadorSemantico(buscador_fake.indice, buscador_fake.embedder, score_minimo=corte)

    resultados = com_limiar.buscar(CONSULTA_LISTAS, k=5)

    assert [r.doc_id for r in resultados] == [sem_limiar[0].doc_id]
    assert com_limiar.buscar("xyzzy plugh termo inexistente", k=5) == []


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
        (CONSULTA_LISTAS, "listas"),
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


def test_bm25_ignora_chunks_sem_termo_em_comum_e_pode_listar_por_chunk(corpus):
    chunks = dividir_em_chunks(corpus, settings.chunk_size, settings.chunk_overlap)
    bm25 = BuscadorBM25(chunks)

    assert bm25.buscar("xyzzy plugh", k=3) == []  # score zero não é resultado
    por_chunk = bm25.buscar(
        "lista append extend insert remove pop", k=4, agrupar_por_documento=False
    )
    chaves = [(r.doc_id, r.indice_chunk) for r in por_chunk]
    assert len(chaves) == len(set(chaves)) == 4
    assert len({doc_id for doc_id, _ in chaves}) < 4


def test_busca_hibrida_funde_os_dois_rankings(buscador_fake):
    hibrido = BuscadorHibrido(buscador_fake)

    resultados = hibrido.buscar(CONSULTA_LISTAS, k=3)

    ids = [r.doc_id for r in resultados]
    assert ids[0] == "listas"
    assert len(ids) == len(set(ids)) == 3
    scores = [r.score for r in resultados]
    assert scores == sorted(scores, reverse=True)
    # Documento presente nos dois rankings soma as duas contribuições do RRF.
    assert resultados[0].score > 1 / (60 + 1)


def test_busca_hibrida_por_chunk_mantem_partes_do_mesmo_documento(buscador_fake):
    hibrido = BuscadorHibrido(buscador_fake)

    resultados = hibrido.buscar(
        "lista append extend insert remove pop sort", k=6, agrupar_por_documento=False
    )

    chaves = [(r.doc_id, r.indice_chunk) for r in resultados]
    assert len(chaves) == len(set(chaves)) == 6
    assert sum(1 for doc_id, _ in chaves if doc_id == "listas") >= 2


def test_busca_hibrida_respeita_o_limiar_do_semantico(buscador_fake):
    estrito = BuscadorSemantico(buscador_fake.indice, buscador_fake.embedder, score_minimo=0.999)

    # Mesmo com termos em comum (o BM25 acharia), nada passa do limiar: fora do domínio.
    assert BuscadorHibrido(estrito).buscar(CONSULTA_LISTAS, k=3) == []


def test_calibracao_do_limiar_compara_os_dois_grupos(buscador_fake):
    grupos = dict(
        consultas=[(CONSULTA_LISTAS, "listas")],
        fora_do_dominio=["xyzzy plugh termo inexistente"],
    )

    sem_limiar = calibrar_score_minimo(buscador_fake, **grupos)
    # O hashing do embedder simulado dá um score pequeno mas não nulo a termos inexistentes.
    assert sem_limiar.maior_fora_do_dominio < sem_limiar.menor_no_dominio
    assert not sem_limiar.separa  # sem limiar configurado não há o que conferir

    com_limiar = calibrar_score_minimo(buscador_fake, score_minimo=sem_limiar.sugestao, **grupos)
    assert com_limiar.separa
    assert sem_limiar.maior_fora_do_dominio < com_limiar.sugestao < sem_limiar.menor_no_dominio


def test_calibracao_exige_buscador_sem_limiar(buscador_fake):
    com_limiar = BuscadorSemantico(buscador_fake.indice, buscador_fake.embedder, score_minimo=0.5)

    with pytest.raises(ValueError, match="sem score_minimo"):
        calibrar_score_minimo(com_limiar)


# ---------------------------------------------------------------- modelo real


@pytest.mark.slow
def test_modelo_real_entende_parafrase():
    """Consulta sem nenhuma palavra do título: só um modelo semântico acerta."""
    embedder = SentenceTransformerEmbedder(settings.embedding_model)
    buscador = BuscadorSemantico(construir_indice(settings.corpus_dir, embedder), embedder)

    resultados = buscador.buscar("repetir um bloco de código para cada elemento", k=3)

    assert "loops-for-while" in [r.doc_id for r in resultados]
