---
title: Módulos, pacotes e ambientes virtuais: organizando e instalando dependências
slug: modulos-pacotes-e-ambientes
tags: python, módulos, pip, ambientes virtuais
source: artigo original escrito para este corpus
---
Todo arquivo `.py` é um módulo, e uma pasta com módulos (tradicionalmente com um `__init__.py`) é um pacote. Você reutiliza código com `import`: `import math` traz o módulo inteiro (`math.sqrt(16)`), `from math import sqrt` traz só o nome, e `import numpy as np` dá um apelido. Evite `from modulo import *`, que polui o namespace e esconde de onde cada nome veio.

A biblioteca padrão já resolve muita coisa sem instalar nada: `os` e `pathlib` para arquivos e caminhos, `json`, `csv`, `datetime`, `re` para expressões regulares, `collections`, `itertools`, `logging`, `argparse` para linhas de comando e `unittest` para testes.

Bibliotecas de terceiros vêm do PyPI, o índice de pacotes do Python, e são instaladas com o `pip`: `pip install requests`. O problema de instalar tudo direto no Python do sistema é que projetos diferentes acabam exigindo versões diferentes da mesma biblioteca, e uma instalação quebra a outra.

A solução é o ambiente virtual: uma instalação isolada do Python por projeto. Crie com `python -m venv .venv`, ative com `source .venv/bin/activate` (Linux e macOS) ou `.venv\Scripts\activate` (Windows) e instale as bibliotecas dentro dele. A pasta `.venv` não vai para o controle de versão; o que se versiona é a lista de dependências.

Essa lista pode ser um `requirements.txt` (gerado com `pip freeze > requirements.txt` e instalado com `pip install -r requirements.txt`) ou, no formato moderno, o arquivo `pyproject.toml`, que descreve o projeto, suas dependências e a configuração das ferramentas em um só lugar.

Ferramentas como `uv` e `poetry` cuidam do ciclo completo: criam o ambiente, resolvem versões compatíveis, gravam um arquivo de lock com as versões exatas (reprodutibilidade) e executam comandos dentro do ambiente (`uv run pytest`). O `uv` em particular é muito rápido e também instala versões do próprio Python.

Boas práticas: um ambiente por projeto, dependências com versões mínimas declaradas, arquivo de lock versionado, e separação entre dependências de execução e de desenvolvimento (testes, lint). Assim qualquer pessoa reproduz o projeto com dois comandos: clonar e sincronizar.
