"""Modelo de domínio da biblioteca virtual."""

import unicodedata

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


def normalizar(texto: str) -> str:
    """Forma de busca de um texto: sem acentos, sem distinção de maiúsculas, sem espaços nas pontas.

    'Aluísio Azevedo' -> 'aluisio azevedo'. Só os acentos (marcas combinantes) são removidos;
    letras de outros alfabetos ficam como estão. O SQLite não sabe fazer isso em SQL (o LIKE
    só ignora maiúsculas em ASCII), então o valor normalizado é guardado em coluna própria.
    """
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).casefold().strip()


class Livro(models.Model):
    """Um livro cadastrado na biblioteca.

    Os quatro campos pedidos no enunciado (título, autor, data de publicação e resumo)
    mais `criado_em`, útil para ordenação estável e auditoria, e duas colunas derivadas
    (`*_normalizado`) que tornam a consulta por título/autor insensível a acentos e caixa.
    """

    titulo = models.CharField("título", max_length=200, db_index=True)
    autor = models.CharField("autor", max_length=200, db_index=True)
    data_publicacao = models.DateField("data de publicação")
    resumo = models.TextField("resumo")
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    # Preenchidas automaticamente (ver `_preencher_campos_de_busca`); nunca editadas à mão.
    titulo_normalizado = models.CharField(max_length=200, db_index=True, editable=False, default="")
    autor_normalizado = models.CharField(max_length=200, db_index=True, editable=False, default="")

    class Meta:
        verbose_name = "livro"
        verbose_name_plural = "livros"
        # Mais recentes primeiro; o desempate por id mantém a paginação determinística.
        ordering = ["-criado_em", "-id"]
        constraints = [
            # O mesmo livro (título + autor + data) não entra duas vezes no catálogo.
            # Edições diferentes têm datas diferentes e continuam permitidas.
            models.UniqueConstraint(
                fields=["titulo_normalizado", "autor_normalizado", "data_publicacao"],
                name="livro_unico_por_titulo_autor_data",
            )
        ]

    def __str__(self) -> str:
        return f"{self.titulo} ({self.autor})"


@receiver(pre_save, sender=Livro)
def _preencher_campos_de_busca(sender, instance: Livro, **kwargs) -> None:
    """Mantém as colunas normalizadas em dia a cada gravação.

    É um signal, e não um `save()` sobrescrito, porque `loaddata` (fixtures) grava sem
    chamar `save()` mas emite `pre_save`; assim o `make seed` também fica pesquisável.
    """
    instance.titulo_normalizado = normalizar(instance.titulo)
    instance.autor_normalizado = normalizar(instance.autor)
