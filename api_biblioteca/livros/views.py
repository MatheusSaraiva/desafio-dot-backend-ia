"""Endpoints da API de livros.

Um único ViewSet cobre o CRUD completo em `/api/livros/`:
- POST   /api/livros/        cadastro (pedido no enunciado)
- GET    /api/livros/        consulta com filtros por título/autor (pedido no enunciado)
- GET    /api/livros/{id}/   detalhe
- PUT/PATCH/DELETE           manutenção, de graça com o ModelViewSet
"""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import viewsets

from .filters import LivroFilter
from .models import Livro
from .serializers import LivroSerializer

EXEMPLO_LIVRO = OpenApiExample(
    "Exemplo de cadastro",
    value={
        "titulo": "Dom Casmurro",
        "autor": "Machado de Assis",
        "data_publicacao": "1899-01-01",
        "resumo": "Bento Santiago relembra a juventude e o casamento com Capitu.",
    },
    request_only=True,
)


@extend_schema_view(
    list=extend_schema(
        summary="Consulta livros por título ou autor",
        description=(
            "Lista paginada (20 por página). Combine `titulo` e `autor` para refinar, "
            "ou use `q` para procurar o mesmo texto nos dois campos. "
            "Ordene com `ordering` (ex.: `ordering=titulo` ou `ordering=-data_publicacao`)."
        ),
    ),
    create=extend_schema(summary="Cadastra um livro", examples=[EXEMPLO_LIVRO]),
    retrieve=extend_schema(summary="Detalha um livro"),
    update=extend_schema(summary="Substitui um livro"),
    partial_update=extend_schema(summary="Atualiza campos de um livro"),
    destroy=extend_schema(summary="Remove um livro"),
)
class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    # DjangoFilterBackend usa esta classe; BuscaLivreFilter (?q=) e OrderingFilter
    # vêm de DEFAULT_FILTER_BACKENDS no settings.
    filterset_class = LivroFilter
    search_fields = ["titulo", "autor"]
    ordering_fields = ["titulo", "autor", "data_publicacao", "criado_em"]
