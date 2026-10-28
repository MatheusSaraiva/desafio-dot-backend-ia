---
title: Geradores e iteradores: produzindo valores sob demanda com yield
slug: geradores-e-iteradores
tags: python, iteração, memória
source: artigo original escrito para este corpus
---
Um iterador é um objeto que entrega um item por vez quando você pede o próximo. É o que está por trás de todo laço `for`: o Python chama `iter()` na coleção para obter um iterador e `next()` repetidamente até receber `StopIteration`. Listas, tuplas, dicionários, strings e arquivos são iteráveis; qualquer classe que implemente `__iter__` e `__next__` também é.

O jeito mais simples de escrever um iterador é com um gerador: uma função que usa `yield` em vez de `return`. Cada `yield` entrega um valor e pausa a função, que continua do mesmo ponto na próxima chamada:

```python
def contagem(ate):
    n = 1
    while n <= ate:
        yield n
        n += 1
```

Chamar `contagem(3)` não executa nada ainda; devolve um objeto gerador. Os valores só são produzidos quando alguém os consome, com `for n in contagem(3)` ou `next()`. Essa avaliação preguiçosa é a grande vantagem: um gerador que lê um arquivo de gigabytes linha a linha, ou que produz uma sequência infinita, ocupa memória constante, enquanto uma lista precisaria guardar tudo de uma vez.

Geradores podem ser encadeados como etapas de um pipeline: um lê linhas, o próximo filtra as relevantes, o seguinte converte os campos. Cada item atravessa todas as etapas antes do próximo ser lido. A expressão geradora, `(x * 2 for x in numeros)`, é a forma compacta de um gerador simples e pode ser passada diretamente para `sum`, `max`, `any` ou `", ".join`.

Um gerador só pode ser percorrido uma vez; depois de esgotado, ele não "volta ao início". Se precisar percorrer de novo, chame a função de novo ou converta para lista. Também não dá para saber o tamanho com `len` nem acessar por índice.

O módulo `itertools` traz blocos prontos para combinar iteradores: `chain` concatena, `islice` fatia, `groupby` agrupa consecutivos, `product` e `combinations` geram combinações. Para quem precisa de controle fino, `yield from` delega para outro gerador, e geradores podem até receber valores com `send()`, base das corrotinas.
