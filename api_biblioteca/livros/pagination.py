"""Paginação das listagens: 20 por página, ajustável pelo cliente até um teto."""

from rest_framework.pagination import PageNumberPagination


class PaginacaoPadrao(PageNumberPagination):
    page_size = 20
    # `?page_size=50` para quem quer mais por página; o teto evita que um cliente
    # peça o catálogo inteiro de uma vez.
    page_size_query_param = "page_size"
    max_page_size = 100
