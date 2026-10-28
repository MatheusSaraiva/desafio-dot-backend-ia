---
title: Dicionários: mapeando chaves a valores
slug: dicionarios
tags: python, estruturas de dados
source: artigo original escrito para este corpus
---
O dicionário (`dict`) associa chaves a valores, como um índice remissivo ou uma agenda telefônica. Ele é criado com chaves: `aluno = {"nome": "Ana", "idade": 29, "curso": "Python"}`. As chaves precisam ser imutáveis (strings, números, tuplas); os valores podem ser qualquer coisa, inclusive outros dicionários e listas.

Para ler um valor, use a chave entre colchetes: `aluno["nome"]`. Se a chave não existir, isso levanta `KeyError`. O método `get` é mais tolerante: `aluno.get("telefone")` devolve `None`, e `aluno.get("telefone", "não informado")` devolve o valor padrão escolhido.

Para incluir ou atualizar, basta atribuir: `aluno["cidade"] = "Florianópolis"`. Se a chave já existe, o valor é substituído. `update` mescla outro dicionário: `aluno.update({"idade": 30, "ativo": True})`. Para remover, use `del aluno["curso"]` ou `aluno.pop("curso")`, que também devolve o valor removido.

Os dicionários mantêm a ordem de inserção. Para percorrer, há três visões: `aluno.keys()` para as chaves, `aluno.values()` para os valores e `aluno.items()` para os pares. O padrão mais comum é `for chave, valor in aluno.items(): print(chave, valor)`.

Verifique a presença de uma chave com `in`: `"idade" in aluno`. Conte as entradas com `len(aluno)`. Uma dict comprehension cria dicionários a partir de sequências: `quadrados = {n: n * n for n in range(5)}`.

Dois utilitários do módulo `collections` evitam código repetitivo. `defaultdict(list)` cria a lista automaticamente na primeira vez que uma chave é usada, ótimo para agrupar itens. `Counter` conta ocorrências: `Counter("banana")` devolve `{"a": 3, "n": 2, "b": 1}`.

Em termos de desempenho, buscar, inserir e remover por chave custa tempo constante em média, graças à tabela hash por trás do dicionário. Por isso ele é a escolha certa sempre que você precisa localizar algo por um identificador em vez de por posição.
