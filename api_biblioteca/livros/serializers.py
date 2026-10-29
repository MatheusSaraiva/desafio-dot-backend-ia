"""Serialização e validação de entrada/saída da API de livros."""

from django.utils import timezone
from rest_framework import serializers

from .models import Livro, normalizar


class LivroSerializer(serializers.ModelSerializer):
    """Representa um livro na API e valida o cadastro.

    Regras além das do modelo:
    - título, autor e resumo não podem ser vazios (espaços são removidos);
    - a data de publicação não pode estar no futuro;
    - não pode existir outro livro com o mesmo título, autor e data (ignorando acentos
      e maiúsculas), para o catálogo não acumular entradas repetidas.
    """

    class Meta:
        model = Livro
        fields = ["id", "titulo", "autor", "data_publicacao", "resumo", "criado_em"]
        read_only_fields = ["id", "criado_em"]

    @staticmethod
    def _texto_obrigatorio(valor: str, campo: str) -> str:
        valor = valor.strip()
        if not valor:
            raise serializers.ValidationError(f"O campo {campo} não pode ser vazio.")
        return valor

    def validate_titulo(self, valor: str) -> str:
        return self._texto_obrigatorio(valor, "título")

    def validate_autor(self, valor: str) -> str:
        return self._texto_obrigatorio(valor, "autor")

    def validate_resumo(self, valor: str) -> str:
        return self._texto_obrigatorio(valor, "resumo")

    def validate_data_publicacao(self, valor):
        # localdate() respeita o fuso configurado (America/Sao_Paulo), evitando falso
        # "futuro" perto da meia-noite.
        if valor > timezone.localdate():
            raise serializers.ValidationError("A data de publicação não pode estar no futuro.")
        return valor

    def validate(self, dados: dict) -> dict:
        """Rejeita duplicatas com uma mensagem clara (400), antes de o banco recusar (500).

        Num PATCH só alguns campos chegam; os demais vêm da instância que está sendo editada.
        """

        def valor(campo: str):
            return dados.get(campo, getattr(self.instance, campo, None))

        repetidos = Livro.objects.filter(
            titulo_normalizado=normalizar(valor("titulo")),
            autor_normalizado=normalizar(valor("autor")),
            data_publicacao=valor("data_publicacao"),
        )
        if self.instance is not None:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError(
                "Já existe um livro cadastrado com este título, autor e data de publicação."
            )
        return dados
