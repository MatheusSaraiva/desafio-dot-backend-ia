---
title: Laços for e while: percorrendo sequências e repetindo tarefas
slug: loops-for-while
tags: python, controle de fluxo, iniciante
source: artigo original escrito para este corpus
---
O laço `for` percorre os itens de qualquer coisa iterável: listas, tuplas, strings, dicionários, arquivos. A sintaxe é direta: `for fruta in frutas: print(fruta)`. Não existe contador manual; o Python entrega um item por vez.

Para repetir um número fixo de vezes, use `range`: `for i in range(5)` gera 0, 1, 2, 3, 4. `range(1, 11)` vai de 1 a 10 e `range(0, 100, 10)` pula de dez em dez. Quando você precisa do índice e do item ao mesmo tempo, `enumerate` resolve: `for posicao, fruta in enumerate(frutas, start=1)`.

Para caminhar por duas sequências em paralelo, use `zip`: `for nome, nota in zip(nomes, notas)`. Para percorrer um dicionário com chave e valor, use `items()`.

O laço `while` repete enquanto uma condição for verdadeira: `while tentativas < 3: ...`. Ele é a escolha quando você não sabe de antemão quantas repetições haverá, como ler entradas do usuário até receber "sair" ou tentar uma conexão até conseguir. Cuidado para sempre alterar algo que faça a condição virar falsa, senão o programa trava em um laço infinito.

Dois comandos controlam o fluxo dentro de qualquer laço. `break` interrompe o laço imediatamente; `continue` pula para a próxima iteração sem executar o resto do bloco. Um `else` depois do laço executa somente se o laço terminar sem `break`, útil para buscas: se o item não foi encontrado, o `else` roda.

Evite modificar uma lista enquanto a percorre, porque os índices se deslocam e itens são pulados. Percorra uma cópia (`for item in lista[:]`) ou construa uma nova lista com os itens que devem ficar.

Se o objetivo do laço é apenas produzir uma lista nova a partir de outra, uma list comprehension costuma ser mais curta e mais legível do que o `for` com `append`.
