---
title: Funções: definição, parâmetros, valores padrão e retorno
slug: funcoes
tags: python, funções, iniciante
source: artigo original escrito para este corpus
---
Uma função agrupa um trecho de código com nome, para ser reutilizado. Ela é definida com `def`, seguido do nome, dos parâmetros entre parênteses e de dois-pontos; o corpo fica indentado. `return` devolve o resultado e encerra a função; sem `return`, ela devolve `None`.

```python
def saudacao(nome, cumprimento="Olá"):
    """Monta uma saudação. A docstring documenta o que a função faz."""
    return f"{cumprimento}, {nome}!"
```

Os parâmetros podem ter valor padrão, como `cumprimento="Olá"`, e então se tornam opcionais na chamada: `saudacao("Ana")` e `saudacao("Ana", "Bom dia")` funcionam. Parâmetros com valor padrão devem vir depois dos obrigatórios. Uma armadilha clássica: nunca use um objeto mutável como valor padrão (`def f(itens=[])`), porque a mesma lista é compartilhada entre todas as chamadas. Use `None` e crie a lista dentro da função.

Argumentos podem ser passados por posição ou por nome: `saudacao(cumprimento="Oi", nome="Ana")`. Passar por nome deixa a chamada mais clara quando há muitos parâmetros. Com um `*` na assinatura, os parâmetros seguintes só aceitam passagem por nome.

Para aceitar uma quantidade variável de argumentos, use `*args` (tupla com os posicionais extras) e `**kwargs` (dicionário com os nomeados extras). Isso é comum em funções que repassam argumentos para outras.

As variáveis criadas dentro da função são locais: deixam de existir quando ela termina. A função enxerga variáveis globais para leitura, mas para alterá-las precisaria da palavra `global`, o que é quase sempre um sinal de que o desenho pode melhorar. Prefira receber tudo por parâmetro e devolver pelo `return`.

Funções são objetos: podem ser guardadas em variáveis, passadas como argumento (como o `key` do `sorted`) e devolvidas por outras funções. Funções pequenas e anônimas podem ser escritas com `lambda`: `lambda x: x * 2`. Uma boa função faz uma coisa só, tem nome que descreve essa coisa e cabe na tela.
