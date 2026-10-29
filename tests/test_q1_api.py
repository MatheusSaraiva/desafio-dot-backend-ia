"""Testes dos endpoints da Questão 1 (API de biblioteca).

Rodam com pytest-django em um SQLite temporário criado por teste, sem servidor externo.
"""

from datetime import date, timedelta

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from livros.models import Livro, normalizar

# Todos os testes deste módulo acessam o banco.
pytestmark = pytest.mark.django_db

URL_LIVROS = "/api/livros/"


def titulos(resposta) -> list[str]:
    return [livro["titulo"] for livro in resposta.data["results"]]


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def payload() -> dict:
    return {
        "titulo": "Dom Casmurro",
        "autor": "Machado de Assis",
        "data_publicacao": "1899-01-01",
        "resumo": "Bento Santiago relembra a juventude e o casamento com Capitu.",
    }


def criar_livro(**campos) -> Livro:
    """Atalho para popular o banco direto pelo ORM (sem passar pela API)."""
    base = {
        "titulo": "Título",
        "autor": "Autor",
        "data_publicacao": date(2000, 1, 1),
        "resumo": "Resumo.",
    }
    return Livro.objects.create(**{**base, **campos})


# ---------------------------------------------------------------- cadastro


def test_cadastro_retorna_201_e_persiste(client, payload):
    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 201
    assert resposta.data["id"] is not None
    assert resposta.data["titulo"] == "Dom Casmurro"
    assert Livro.objects.filter(titulo="Dom Casmurro", autor="Machado de Assis").exists()


def test_cadastro_normaliza_espacos(client, payload):
    payload["titulo"] = "  Dom Casmurro  "
    payload["autor"] = " Machado de Assis "

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 201
    assert resposta.data["titulo"] == "Dom Casmurro"
    assert resposta.data["autor"] == "Machado de Assis"


@pytest.mark.parametrize("campo", ["titulo", "autor", "data_publicacao", "resumo"])
def test_cadastro_sem_campo_obrigatorio_retorna_400(client, payload, campo):
    del payload[campo]

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 400
    assert campo in resposta.data


def test_cadastro_com_titulo_em_branco_retorna_400(client, payload):
    payload["titulo"] = "   "

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 400
    assert "titulo" in resposta.data


def test_cadastro_com_data_futura_retorna_400(client, payload):
    payload["data_publicacao"] = (date.today() + timedelta(days=1)).isoformat()

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 400
    assert "futuro" in str(resposta.data["data_publicacao"][0])


def test_cadastro_com_data_em_formato_invalido_retorna_400(client, payload):
    payload["data_publicacao"] = "01/01/1899"

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 400
    assert "data_publicacao" in resposta.data


def test_cadastro_duplicado_retorna_400_mesmo_com_acentos_e_caixa_diferentes(client, payload):
    assert client.post(URL_LIVROS, payload, format="json").status_code == 201
    payload["titulo"] = "  DOM CASMURRO "
    payload["autor"] = "machado de assis"

    resposta = client.post(URL_LIVROS, payload, format="json")

    assert resposta.status_code == 400
    assert "Já existe" in str(resposta.data["non_field_errors"][0])
    assert Livro.objects.count() == 1


def test_mesmo_titulo_e_autor_com_outra_data_e_aceito(client, payload):
    """Outra edição é outro registro."""
    assert client.post(URL_LIVROS, payload, format="json").status_code == 201
    payload["data_publicacao"] = "1900-05-01"

    assert client.post(URL_LIVROS, payload, format="json").status_code == 201


# ---------------------------------------------------------------- consulta


def test_lista_vazia(client):
    resposta = client.get(URL_LIVROS)

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0
    assert resposta.data["results"] == []


def test_lista_e_paginada_com_20_por_pagina(client):
    for i in range(25):
        criar_livro(titulo=f"Livro {i:02d}")

    pagina1 = client.get(URL_LIVROS)
    pagina2 = client.get(URL_LIVROS, {"page": 2})

    assert pagina1.data["count"] == 25
    assert len(pagina1.data["results"]) == 20
    assert pagina1.data["next"] is not None
    assert len(pagina2.data["results"]) == 5


def test_consulta_por_titulo_parcial_sem_distinguir_maiusculas(client):
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")
    criar_livro(titulo="O Cortiço", autor="Aluísio Azevedo")

    resposta = client.get(URL_LIVROS, {"titulo": "CASMURRO"})

    assert resposta.status_code == 200
    assert [livro["titulo"] for livro in resposta.data["results"]] == ["Dom Casmurro"]


def test_consulta_por_autor(client):
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")
    criar_livro(titulo="Quincas Borba", autor="Machado de Assis")
    criar_livro(titulo="O Cortiço", autor="Aluísio Azevedo")

    resposta = client.get(URL_LIVROS, {"autor": "machado"})

    titulos = {livro["titulo"] for livro in resposta.data["results"]}
    assert titulos == {"Dom Casmurro", "Quincas Borba"}


def test_consulta_combina_titulo_e_autor(client):
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")
    criar_livro(titulo="Quincas Borba", autor="Machado de Assis")

    resposta = client.get(URL_LIVROS, {"autor": "machado", "titulo": "quincas"})

    assert [livro["titulo"] for livro in resposta.data["results"]] == ["Quincas Borba"]


def test_busca_livre_q_procura_em_titulo_e_autor(client):
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")
    criar_livro(titulo="Machado e a Ironia", autor="Fulano de Tal")
    criar_livro(titulo="O Cortiço", autor="Aluísio Azevedo")

    resposta = client.get(URL_LIVROS, {"q": "machado"})

    titulos = {livro["titulo"] for livro in resposta.data["results"]}
    assert titulos == {"Dom Casmurro", "Machado e a Ironia"}


def test_consulta_ignora_acentos_e_maiusculas(client):
    criar_livro(titulo="O Cortiço", autor="Aluísio Azevedo")
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")

    assert titulos(client.get(URL_LIVROS, {"titulo": "cortico"})) == ["O Cortiço"]
    assert titulos(client.get(URL_LIVROS, {"titulo": "CORTIÇO"})) == ["O Cortiço"]
    assert titulos(client.get(URL_LIVROS, {"autor": "ALUÍSIO"})) == ["O Cortiço"]
    assert titulos(client.get(URL_LIVROS, {"autor": "aluisio azevedo"})) == ["O Cortiço"]


def test_busca_livre_ignora_acentos(client):
    criar_livro(titulo="Memórias Póstumas de Brás Cubas", autor="Machado de Assis")
    criar_livro(titulo="O Cortiço", autor="Aluísio Azevedo")

    resposta = client.get(URL_LIVROS, {"q": "memorias postumas"})

    assert titulos(resposta) == ["Memórias Póstumas de Brás Cubas"]


def test_consulta_sem_resultado_retorna_lista_vazia(client):
    criar_livro(titulo="Dom Casmurro")

    resposta = client.get(URL_LIVROS, {"titulo": "inexistente"})

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_page_size_e_configuravel_pelo_cliente(client):
    for i in range(5):
        criar_livro(titulo=f"Livro {i}")

    assert len(client.get(URL_LIVROS, {"page_size": 2}).data["results"]) == 2
    assert client.get(URL_LIVROS, {"page_size": 2}).data["next"] is not None
    # Acima do teto (100) o valor é reduzido, não rejeitado.
    assert client.get(URL_LIVROS, {"page_size": 1000}).data["count"] == 5


def test_filtro_por_ano_e_ordenacao(client):
    criar_livro(titulo="B", data_publicacao=date(1899, 1, 1))
    criar_livro(titulo="A", data_publicacao=date(1899, 6, 1))
    criar_livro(titulo="C", data_publicacao=date(1956, 1, 1))

    resposta = client.get(URL_LIVROS, {"ano": 1899, "ordering": "titulo"})

    assert [livro["titulo"] for livro in resposta.data["results"]] == ["A", "B"]


# ---------------------------------------------------------------- detalhe e manutenção


def test_detalhe_retorna_livro(client):
    livro = criar_livro(titulo="Vidas Secas", autor="Graciliano Ramos")

    resposta = client.get(f"{URL_LIVROS}{livro.id}/")

    assert resposta.status_code == 200
    assert resposta.data["autor"] == "Graciliano Ramos"


def test_detalhe_inexistente_retorna_404(client):
    resposta = client.get(f"{URL_LIVROS}999/")

    assert resposta.status_code == 404


def test_atualizacao_parcial(client):
    livro = criar_livro(titulo="Vidas Seca")

    resposta = client.patch(f"{URL_LIVROS}{livro.id}/", {"titulo": "Vidas Secas"}, format="json")

    assert resposta.status_code == 200
    livro.refresh_from_db()
    assert livro.titulo == "Vidas Secas"
    assert livro.titulo_normalizado == "vidas secas"


def test_atualizacao_que_viraria_duplicata_retorna_400(client):
    criar_livro(titulo="Dom Casmurro", autor="Machado de Assis", data_publicacao=date(1899, 1, 1))
    outro = criar_livro(
        titulo="Rascunho", autor="Machado de Assis", data_publicacao=date(1899, 1, 1)
    )

    resposta = client.patch(f"{URL_LIVROS}{outro.id}/", {"titulo": "dom casmurro"}, format="json")

    assert resposta.status_code == 400
    assert "non_field_errors" in resposta.data


def test_atualizacao_do_proprio_registro_nao_conta_como_duplicata(client):
    livro = criar_livro(titulo="Dom Casmurro", autor="Machado de Assis")

    resposta = client.patch(f"{URL_LIVROS}{livro.id}/", {"resumo": "Novo resumo."}, format="json")

    assert resposta.status_code == 200


def test_remocao(client):
    livro = criar_livro()

    resposta = client.delete(f"{URL_LIVROS}{livro.id}/")

    assert resposta.status_code == 204
    assert not Livro.objects.filter(id=livro.id).exists()


# ---------------------------------------------------------------- documentação e modelo


def test_schema_openapi_e_docs_disponiveis(client):
    schema = client.get("/api/schema/")

    assert schema.status_code == 200
    assert client.get("/api/docs/").status_code == 200
    # Os parâmetros de consulta aparecem documentados, com a descrição dos filtros.
    for parametro in (b"name: titulo", b"name: autor", b"name: q", b"name: page_size"):
        assert parametro in schema.content


def test_representacao_textual_do_modelo():
    livro = criar_livro(titulo="Iracema", autor="José de Alencar")

    assert str(livro) == "Iracema (José de Alencar)"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Aluísio Azevedo", "aluisio azevedo"),
        ("  O CORTIÇO ", "o cortico"),
        ("Ñandu", "nandu"),
        ("日本語", "日本語"),  # outros alfabetos ficam como estão
    ],
)
def test_normalizar_remove_acentos_e_caixa(texto, esperado):
    assert normalizar(texto) == esperado


def test_campos_normalizados_sao_preenchidos_ao_salvar():
    livro = criar_livro(titulo="  Memórias Póstumas ", autor="Machado de ASSIS")

    assert livro.titulo_normalizado == "memorias postumas"
    assert livro.autor_normalizado == "machado de assis"


def test_fixture_de_exemplo_carrega_e_fica_pesquisavel(client):
    """`make seed` usa loaddata, que não chama save(): o signal precisa cobrir esse caminho."""
    call_command("loaddata", "livros", verbosity=0)

    assert Livro.objects.count() == 10
    assert titulos(client.get(URL_LIVROS, {"autor": "aluisio"})) == ["O Cortiço"]
