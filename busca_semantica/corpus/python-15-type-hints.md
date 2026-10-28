---
title: Type hints: anotando tipos para código mais claro e verificável
slug: type-hints
tags: python, tipagem, qualidade
source: artigo original escrito para este corpus
---
Python é dinamicamente tipado, mas desde a versão 3.5 permite anotar os tipos esperados de parâmetros, retornos e variáveis. As anotações não mudam a execução; servem para documentação, para o autocompletar do editor e para verificadores estáticos como `mypy` e `pyright`, que apontam erros antes de o código rodar.

```python
def calcular_media(notas: list[float], casas: int = 2) -> float:
    return round(sum(notas) / len(notas), casas)
```

Lê-se: `notas` é uma lista de floats, `casas` é um inteiro com padrão 2 e a função devolve um float. Os tipos básicos são `int`, `float`, `str`, `bool`, `bytes` e `None`. Coleções usam colchetes: `list[str]`, `dict[str, int]`, `tuple[int, int]`, `set[str]`. Um valor que pode ser de dois tipos usa a barra: `int | None` significa "inteiro ou None", o caso típico de parâmetros opcionais.

Para tipos mais abstratos, o módulo `typing` e `collections.abc` oferecem `Iterable`, `Sequence`, `Mapping`, `Callable` e `Protocol`. Anotar um parâmetro como `Iterable[str]` em vez de `list[str]` aceita qualquer coisa iterável e documenta que a função só vai percorrer os itens. Um `Protocol` descreve uma interface pelo comportamento ("tem um método `buscar`"), sem exigir herança, no espírito do duck typing.

Variáveis podem ser anotadas (`total: int = 0`), e `dataclass` e Pydantic usam as anotações para gerar código: o Pydantic valida dados em tempo de execução a partir delas, o que o tornou padrão em APIs com FastAPI e em configurações com `pydantic-settings`.

Outras ferramentas úteis: `TypedDict` descreve a forma de um dicionário, `Literal["asc", "desc"]` restringe a valores específicos, `TypeAlias` dá nome a tipos compostos, e `Annotated` anexa metadados a um tipo (o Typer e o FastAPI usam isso para descrever parâmetros).

Type hints valem mais em código que outras pessoas vão manter: assinaturas de funções públicas, modelos de dados e fronteiras entre módulos. Não é preciso anotar cada variável local. Rode o verificador no CI e trate os avisos como se fossem testes falhando: muitos bugs de "None não tem atributo x" desaparecem antes de chegar à produção.
