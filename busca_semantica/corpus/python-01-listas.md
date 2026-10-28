---
title: Listas em Python: criando e manipulando coleções ordenadas
slug: listas
tags: python, estruturas de dados, iniciante
source: artigo original escrito para este corpus
---
A lista é a estrutura de dados mais usada em Python. Ela guarda uma sequência ordenada de itens, aceita itens de tipos diferentes e pode crescer ou encolher a qualquer momento. Para criar uma lista, use colchetes: `frutas = ["maçã", "banana", "uva"]`. Uma lista vazia é só `[]` ou `list()`.

Para adicionar um item no final, use `append`: `frutas.append("manga")`. Para adicionar vários itens de uma vez, use `extend`: `frutas.extend(["pera", "kiwi"])`. Se quiser inserir em uma posição específica, `insert(posicao, item)` faz isso: `frutas.insert(0, "laranja")` coloca a laranja no início.

Os itens são acessados pelo índice, que começa em zero: `frutas[0]` é o primeiro item e `frutas[-1]` é o último. O fatiamento (slicing) devolve uma sublista: `frutas[1:3]` pega os itens das posições 1 e 2. Para saber quantos itens a lista tem, use `len(frutas)`.

Para remover itens há três caminhos. `remove(valor)` tira a primeira ocorrência daquele valor; `pop()` remove e devolve o último item (ou o item do índice informado, como em `pop(0)`); `del frutas[2]` apaga pela posição. Para verificar se um item está na lista, use `in`: `"uva" in frutas` devolve `True` ou `False`.

Ordenar é simples: `frutas.sort()` ordena a própria lista, enquanto `sorted(frutas)` devolve uma nova lista ordenada e deixa a original intacta. Os dois aceitam `reverse=True` e o parâmetro `key`, que recebe uma função para definir o critério, por exemplo `sorted(frutas, key=len)` para ordenar pelo tamanho do texto.

Um detalhe importante: a lista é mutável e passada por referência. Se você fizer `copia = frutas`, as duas variáveis apontam para a mesma lista, e alterar uma altera a outra. Para copiar de verdade, use `frutas.copy()` ou `frutas[:]`.

Resumo das operações mais comuns: criar com `[]`, adicionar com `append`, contar com `len`, acessar com `[indice]`, remover com `remove`/`pop`, ordenar com `sort`/`sorted` e percorrer os itens com um laço `for`.
