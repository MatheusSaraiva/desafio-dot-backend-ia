---
title: Arquivos: ler e escrever texto, CSV e JSON
slug: arquivos
tags: python, arquivos, entrada e saída
source: artigo original escrito para este corpus
---
Para abrir um arquivo, use `open` dentro de um bloco `with`. O `with` garante que o arquivo é fechado ao final, mesmo que aconteça um erro no meio:

```python
with open("notas.txt", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()
```

O segundo argumento de `open` é o modo: `"r"` para leitura (padrão), `"w"` para escrita (apaga o conteúdo anterior), `"a"` para acrescentar ao final e `"b"` combinado com os anteriores para arquivos binários. Informe sempre `encoding="utf-8"` em arquivos de texto.

Há três formas de ler: `read()` devolve tudo em uma string; `readlines()` devolve uma lista de linhas; e percorrer o próprio objeto com `for linha in arquivo` lê uma linha por vez, sem carregar o arquivo inteiro na memória, o que é ideal para arquivos grandes. Cada linha vem com a quebra `\n` no final; use `linha.rstrip("\n")` para removê-la.

Para escrever, use `write`: `arquivo.write("primeira linha\n")`. Ele não adiciona a quebra de linha automaticamente. `print(texto, file=arquivo)` é uma alternativa que adiciona.

Arquivos CSV (valores separados por vírgula) são lidos com o módulo `csv`. O `csv.DictReader` devolve cada linha como um dicionário cujas chaves são os nomes das colunas do cabeçalho: `for linha in csv.DictReader(arquivo): print(linha["nome"])`. Para gravar, `csv.DictWriter` recebe a lista de colunas e grava dicionários. Para arquivos CSV grandes ou análises, a biblioteca pandas lê tudo com `pd.read_csv`.

Arquivos JSON são tratados pelo módulo `json`: `json.load(arquivo)` converte o conteúdo em dicionários e listas do Python; `json.dump(dados, arquivo, ensure_ascii=False, indent=2)` grava de forma legível. Para strings em vez de arquivos, use `json.loads` e `json.dumps`.

Para caminhos, prefira `pathlib.Path` a strings: `Path("dados") / "notas.txt"` monta o caminho de forma portátil, `.exists()` verifica se existe, `.read_text()` e `.write_text()` leem e gravam texto em uma linha e `.glob("*.csv")` lista arquivos por padrão.
