---
title: Testes automatizados com pytest: escrevendo e organizando testes
slug: testes-com-pytest
tags: python, testes, qualidade
source: artigo original escrito para este corpus
---
Testes automatizados verificam, a cada mudança, que o código continua fazendo o que deveria. O `pytest` é o framework mais usado em Python porque exige pouco: um arquivo cujo nome começa com `test_`, funções que começam com `test_` e o `assert` comum da linguagem.

```python
from biblioteca import calcular_media


def test_media_de_duas_notas():
    assert calcular_media([8.0, 6.0]) == 7.0


def test_lista_vazia_levanta_erro():
    with pytest.raises(ZeroDivisionError):
        calcular_media([])
```

Rode `pytest` na raiz do projeto e ele descobre os testes sozinho. Quando um `assert` falha, o pytest mostra os valores envolvidos, o que facilita entender o problema sem `print`. Opções úteis: `-q` para saída resumida, `-x` para parar na primeira falha, `-k nome` para rodar só testes cujo nome contém um texto e `-m marcador` para filtrar por marcadores.

Fixtures preparam o cenário de um teste e são injetadas pelo nome do parâmetro. Uma função decorada com `@pytest.fixture` que devolve um cliente HTTP, uma conexão com banco temporário ou dados de exemplo pode ser compartilhada por vários testes; o `scope` controla se ela é criada por teste, por módulo ou por sessão. O `tmp_path` é uma fixture embutida que dá uma pasta temporária limpa, e o `monkeypatch` permite trocar atributos, variáveis de ambiente e funções durante um teste.

`@pytest.mark.parametrize` roda o mesmo teste com vários conjuntos de entrada, cada um aparecendo como um caso separado no relatório. Marcadores personalizados como `@pytest.mark.slow` ou `@pytest.mark.integration` permitem separar testes rápidos e offline dos que dependem de serviços externos ou de modelos pesados, e a configuração em `pyproject.toml` define quais rodam por padrão.

Um bom teste é independente (não depende da ordem nem de outros testes), rápido e com nome que descreve o comportamento esperado, como `test_cadastro_com_data_futura_retorna_400`. Testes de unidade isolam uma função ou classe, substituindo dependências externas por dublês (fakes, mocks). Testes de integração exercitam várias partes juntas, como uma API com seu banco. Rode os dois tipos no CI, e trate um teste quebrado como a prioridade do dia.
