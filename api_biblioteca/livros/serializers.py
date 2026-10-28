"""Serialização e validação de entrada/saída da API de livros."""

from django.utils import timezone
from rest_framework import serializers

from .models import Livro


class LivroSerializer(serializers.ModelSerializer):
    """Representa um livro na API e valida o cadastro.

    Regras além das do modelo:
    - título, autor e resumo não podem ser vazios (espaços são removidos);
    - a data de publicação não pode estar no futuro.
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
