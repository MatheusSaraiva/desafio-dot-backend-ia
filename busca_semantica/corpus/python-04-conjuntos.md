---
title: Conjuntos (set): elementos únicos e operações de teoria dos conjuntos
slug: conjuntos
tags: python, estruturas de dados
source: artigo original escrito para este corpus
---
Um conjunto (`set`) é uma coleção sem ordem e sem elementos repetidos. Ele é criado com chaves ou com `set()`: `tags = {"python", "backend", "api"}`. Atenção: `{}` cria um dicionário vazio, então um conjunto vazio é sempre `set()`.

O uso mais frequente é eliminar duplicatas de uma lista: `unicos = set(["a", "b", "a", "c"])` devolve `{"a", "b", "c"}`. Se precisar voltar para lista, `list(unicos)`. Se a ordem original importar, uma alternativa é `list(dict.fromkeys(itens))`, que remove repetidos preservando a primeira ocorrência.

Testar se um elemento pertence ao conjunto é extremamente rápido, independentemente do tamanho: `"api" in tags`. Esse é o motivo de usar `set` em vez de lista quando a operação principal é "está ou não está": verificar e-mails já processados, ids já vistos, palavras proibidas.

Os métodos `add` e `discard` incluem e removem elementos (`discard` não reclama se o elemento não existir; `remove` levanta `KeyError`). `len` conta os elementos e o laço `for` percorre todos, sem ordem garantida.

O ponto forte são as operações de teoria dos conjuntos, com operadores ou métodos equivalentes: união `a | b` (`a.union(b)`), interseção `a & b` (`a.intersection(b)`), diferença `a - b` (`a.difference(b)`) e diferença simétrica `a ^ b`. Perguntas como "quais alunos fizeram o curso A mas não o B" viram uma linha: `fez_a - fez_b`.

Também há comparações: `a <= b` verifica se `a` é subconjunto de `b` e `a.isdisjoint(b)` verifica se não há elementos em comum.

Os elementos precisam ser imutáveis (hasháveis): strings, números e tuplas servem; listas e dicionários não. Se você precisar de um conjunto imutável, por exemplo para usar como chave de dicionário, use `frozenset`.
