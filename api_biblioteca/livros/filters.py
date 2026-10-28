"""Filtros de consulta da API de livros.

Duas formas de consultar, as duas pedidas no enunciado ("por título ou autor"):
- filtros nomeados: `?titulo=casmurro`, `?autor=machado` (podem ser combinados);
- busca livre: `?q=machado` procura em título E autor ao mesmo tempo.
"""

import django_filters
from rest_framework.filters import SearchFilter

from .models import Livro


class LivroFilter(django_filters.FilterSet):
    """Filtros nomeados. `icontains` = busca parcial sem distinguir maiúsculas."""

    titulo = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Parte do título, sem distinção de maiúsculas/minúsculas.",
    )
    autor = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Parte do nome do autor, sem distinção de maiúsculas/minúsculas.",
    )
    ano = django_filters.NumberFilter(
        field_name="data_publicacao",
        lookup_expr="year",
        help_text="Ano de publicação exato.",
    )
    publicado_apos = django_filters.DateFilter(
        field_name="data_publicacao",
        lookup_expr="gte",
        help_text="Data mínima de publicação (AAAA-MM-DD).",
    )
    publicado_antes = django_filters.DateFilter(
        field_name="data_publicacao",
        lookup_expr="lte",
        help_text="Data máxima de publicação (AAAA-MM-DD).",
    )

    class Meta:
        model = Livro
        fields = ["titulo", "autor", "ano", "publicado_apos", "publicado_antes"]


class BuscaLivreFilter(SearchFilter):
    """SearchFilter do DRF com o parâmetro renomeado de `search` para `q`."""

    search_param = "q"
    search_title = "Busca livre"
    search_description = "Texto procurado em título e autor ao mesmo tempo (parcial)."
