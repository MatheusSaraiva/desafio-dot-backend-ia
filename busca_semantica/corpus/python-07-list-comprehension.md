---
title: List comprehension: construindo listas de forma compacta
slug: list-comprehension
tags: python, listas, idiomático
source: artigo original escrito para este corpus
---
A list comprehension é uma sintaxe para criar uma lista nova a partir de uma sequência existente, em uma única expressão. O padrão tradicional com laço e `append` fica assim:

```python
quadrados = []
for n in range(10):
    quadrados.append(n * n)
```

A versão com comprehension diz a mesma coisa de forma mais direta: `quadrados = [n * n for n in range(10)]`. Lê-se "a lista de n ao quadrado para cada n no intervalo". A estrutura é sempre `[expressao for item in iteravel]`.

Um `if` no final filtra os itens: `pares = [n for n in range(10) if n % 2 == 0]`. Um `if`/`else` antes do `for` transforma cada item de acordo com uma condição: `rotulos = ["par" if n % 2 == 0 else "ímpar" for n in numeros]`.

Comprehensions são comuns para transformar dados: extrair um campo de uma lista de dicionários (`nomes = [aluno["nome"] for aluno in alunos]`), limpar strings (`[s.strip().lower() for s in linhas]`) ou converter tipos (`[int(x) for x in "1 2 3".split()]`).

A mesma ideia existe para dicionários e conjuntos: `{palavra: len(palavra) for palavra in palavras}` cria um dict e `{p.lower() for p in palavras}` cria um set sem repetidos. Com parênteses, `(n * n for n in range(10))`, você obtém uma expressão geradora, que produz os valores sob demanda em vez de montar a lista inteira na memória.

É possível aninhar laços (`[x * y for x in a for y in b]`), mas a legibilidade cai rápido. A regra prática: se a comprehension não cabe confortavelmente em uma ou duas linhas, ou se precisa de mais de uma condição, volte para o laço `for` explícito. Comprehensions existem para deixar o código mais claro, não mais curto a qualquer custo.

Em desempenho, a comprehension costuma ser um pouco mais rápida do que o laço com `append`, porque evita a chamada de método a cada iteração, mas a principal razão para usá-la é a clareza de intenção: quem lê entende de imediato que uma lista está sendo construída a partir de outra.
