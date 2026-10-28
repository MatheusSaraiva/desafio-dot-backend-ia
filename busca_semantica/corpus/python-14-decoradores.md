---
title: Decoradores: adicionando comportamento a funções sem alterar seu código
slug: decoradores
tags: python, funções, avançado
source: artigo original escrito para este corpus
---
Um decorador é uma função que recebe outra função e devolve uma versão "embrulhada" dela, com algum comportamento extra antes ou depois. A sintaxe com `@` é só açúcar: escrever `@medir_tempo` acima de `def processar()` equivale a `processar = medir_tempo(processar)`.

```python
import functools, time


def medir_tempo(funcao):
    @functools.wraps(funcao)
    def embrulho(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcao(*args, **kwargs)
        print(f"{funcao.__name__} levou {time.perf_counter() - inicio:.3f}s")
        return resultado

    return embrulho
```

O `embrulho` aceita qualquer combinação de argumentos (`*args`, `**kwargs`), repassa para a função original e devolve o resultado dela. O `functools.wraps` copia nome, docstring e assinatura da função original para o embrulho; sem ele, `processar.__name__` viraria "embrulho" e ferramentas de documentação e depuração se perderiam.

Decoradores são a forma idiomática de aplicar preocupações transversais: registrar logs, medir tempo, cachear resultados, verificar permissões, tentar novamente em caso de falha, validar argumentos. O código da função fica focado na regra de negócio e o comportamento extra fica em um só lugar, reutilizável.

A biblioteca padrão já traz vários: `@functools.lru_cache` memoriza resultados de chamadas repetidas, `@functools.cache` é a versão sem limite, `@property` transforma método em atributo, `@staticmethod` e `@classmethod` mudam como um método recebe o contexto, e `@dataclass` gera métodos de uma classe. Frameworks usam decoradores para registrar rotas (`@app.get("/livros")` no FastAPI) e tarefas (`@shared_task` no Celery).

Para um decorador que aceita parâmetros, como `@tentar_novamente(vezes=3)`, é preciso mais uma camada: uma função que recebe os parâmetros e devolve o decorador propriamente dito. Classes também podem ser decoradas, e um decorador pode ser implementado como uma classe com `__call__`.

Dois cuidados: mantenha os decoradores simples e previsíveis, porque eles escondem comportamento de quem lê apenas a função decorada; e lembre-se de que a ordem importa quando há vários empilhados: o decorador mais próximo da função é aplicado primeiro.
