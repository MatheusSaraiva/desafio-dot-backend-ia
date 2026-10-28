---
title: Tuplas e imutabilidade: quando usar uma tupla em vez de uma lista
slug: tuplas-e-imutabilidade
tags: python, estruturas de dados
source: artigo original escrito para este corpus
---
Uma tupla é uma sequência ordenada, como a lista, com uma diferença decisiva: ela é imutável. Depois de criada, não dá para adicionar, remover nem trocar elementos. Tuplas são escritas com parênteses: `ponto = (10, 20)`. Os parênteses são opcionais em muitos contextos (`ponto = 10, 20` também funciona), mas uma tupla de um único elemento precisa da vírgula: `(10,)`.

A imutabilidade traz três vantagens práticas. Primeiro, segurança: dados que não devem mudar, como coordenadas, configurações ou datas, ficam protegidos de alterações acidentais. Segundo, desempenho: tuplas ocupam menos memória e são um pouco mais rápidas de criar que listas. Terceiro, tuplas podem ser usadas como chave de dicionário e como elemento de conjunto, porque são "hasháveis"; listas não podem.

Um uso muito comum é o desempacotamento: `x, y = ponto` atribui 10 a `x` e 20 a `y`. Funções que precisam devolver mais de um valor costumam devolver uma tupla: `return minimo, maximo`. Trocar o valor de duas variáveis fica elegante: `a, b = b, a`.

Para acessar elementos, use o índice como na lista: `ponto[0]`. Fatiamento, `len`, `in` e o laço `for` também funcionam. Os únicos métodos disponíveis são `count` e `index`, justamente porque nada que altere a tupla faz sentido.

Quando os campos têm significado, a `namedtuple` do módulo `collections` (ou um `dataclass(frozen=True)`) deixa o código mais legível: `Ponto = namedtuple("Ponto", ["x", "y"])` permite escrever `p.x` em vez de `p[0]`.

Regra prática: use lista para coleções homogêneas que mudam ao longo do programa (uma fila de tarefas, resultados acumulados) e tupla para registros fixos e heterogêneos (um par latitude/longitude, uma linha de tabela, uma versão como `(3, 13, 0)`).
