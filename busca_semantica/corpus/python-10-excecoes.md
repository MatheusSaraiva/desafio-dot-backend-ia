---
title: Exceções: tratando erros com try, except, else e finally
slug: excecoes
tags: python, erros, controle de fluxo
source: artigo original escrito para este corpus
---
Quando algo dá errado em tempo de execução, o Python levanta uma exceção: dividir por zero gera `ZeroDivisionError`, acessar uma chave inexistente gera `KeyError`, converter "abc" para inteiro gera `ValueError`, abrir um arquivo que não existe gera `FileNotFoundError`. Se ninguém tratar a exceção, o programa para e mostra o traceback.

O bloco `try`/`except` permite reagir ao erro em vez de deixar o programa quebrar:

```python
try:
    idade = int(entrada)
except ValueError:
    print("Digite um número inteiro.")
```

Capture sempre a exceção mais específica possível. Um `except Exception` genérico (ou pior, `except:` sem nada) esconde erros de programação que você gostaria de ver. É possível tratar vários tipos em um só bloco, `except (ValueError, TypeError):`, ou ter vários `except` em sequência. Para usar o objeto da exceção, por exemplo para registrar a mensagem, escreva `except ValueError as erro:`.

O `else` executa só se o `try` terminar sem exceção, e o `finally` executa sempre, com ou sem erro: é o lugar para liberar recursos, como fechar conexões. Para arquivos, o `with` já faz esse papel.

Para sinalizar um erro no seu próprio código, use `raise`: `raise ValueError("A data de publicação não pode estar no futuro.")`. Crie exceções próprias herdando de `Exception` quando quiser que quem chama consiga distinguir os erros do seu módulo: `class SaldoInsuficienteError(Exception): pass`. Ao relançar uma exceção a partir de outra, `raise NovoErro(...) from erro_original` preserva a causa no traceback.

Uma regra de ouro: trate a exceção onde você consegue fazer algo útil a respeito (tentar de novo, usar um valor padrão, informar o usuário) e deixe-a subir quando não consegue. Exceções não são apenas para falhas: `StopIteration`, por exemplo, é o mecanismo normal que encerra um laço `for`.

Para depurar, o módulo `traceback` e o `logging.exception` registram a pilha completa. E lembre-se de que o estilo do Python é "é mais fácil pedir perdão do que permissão": tentar a operação e tratar a exceção costuma ser mais claro do que checar todas as condições antes.
