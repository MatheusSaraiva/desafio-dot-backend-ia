"""Modelo de domínio da biblioteca virtual."""

from django.db import models


class Livro(models.Model):
    """Um livro cadastrado na biblioteca.

    Os quatro campos pedidos no enunciado (título, autor, data de publicação e resumo)
    mais `criado_em`, útil para ordenação estável e auditoria.
    Título e autor têm índice porque são os campos de consulta da API.
    """

    titulo = models.CharField("título", max_length=200, db_index=True)
    autor = models.CharField("autor", max_length=200, db_index=True)
    data_publicacao = models.DateField("data de publicação")
    resumo = models.TextField("resumo")
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "livro"
        verbose_name_plural = "livros"
        # Mais recentes primeiro; o desempate por id mantém a paginação determinística.
        ordering = ["-criado_em", "-id"]

    def __str__(self) -> str:
        return f"{self.titulo} ({self.autor})"
