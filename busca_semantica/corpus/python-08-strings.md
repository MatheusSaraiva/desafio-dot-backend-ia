---
title: Strings e f-strings: manipulando e formatando texto
slug: strings-e-fstrings
tags: python, strings, formatação
source: artigo original escrito para este corpus
---
Strings são sequências imutáveis de caracteres, escritas entre aspas simples ou duplas. Métodos de string nunca alteram a original; sempre devolvem uma string nova. Os mais usados no dia a dia são `strip` (remove espaços das pontas), `lower` e `upper` (caixa), `replace` (substitui trechos), `split` (quebra em lista por um separador) e `join` (junta uma lista de strings com um separador: `", ".join(nomes)`).

Para montar textos com valores de variáveis, a forma recomendada é a f-string: um `f` antes das aspas e as expressões entre chaves. `f"Olá, {nome}! Você tem {idade} anos."` substitui as chaves pelos valores. Dentro das chaves vale qualquer expressão: `f"Total: {preco * quantidade}"` ou `f"{nome.upper()}"`.

As f-strings aceitam especificações de formato depois de dois-pontos. `f"{valor:.2f}"` mostra duas casas decimais; `f"{numero:,}"` separa milhares; `f"{texto:>10}"` alinha à direita em 10 colunas; `f"{percentual:.1%}"` formata como porcentagem. Para depuração, `f"{variavel=}"` imprime o nome e o valor.

Alternativas mais antigas ainda aparecem em código legado: `"Olá, {}".format(nome)` e `"Olá, %s" % nome`. Funcionam, mas a f-string é mais rápida e mais legível.

Como string é sequência, índice e fatiamento funcionam: `texto[0]` é o primeiro caractere, `texto[-1]` o último e `texto[::-1]` inverte o texto. `len(texto)` conta os caracteres e `in` verifica se um trecho existe: `"erro" in mensagem`.

Outros métodos úteis: `startswith`/`endswith` para prefixo e sufixo, `find` para localizar a posição de um trecho (devolve -1 se não achar), `isdigit` para testar se só há dígitos e `title` para capitalizar palavras.

Strings em Python são Unicode, então acentos e emojis são caracteres normais. Ao ler ou gravar arquivos, informe `encoding="utf-8"` para evitar surpresas entre sistemas operacionais. Para textos de várias linhas, use aspas triplas: `"""..."""`.
