---
title: Classes e objetos: orientação a objetos, herança e dataclasses
slug: classes-e-objetos
tags: python, orientação a objetos
source: artigo original escrito para este corpus
---
Uma classe descreve um tipo de objeto: quais dados ele guarda (atributos) e o que ele sabe fazer (métodos). A instância é um objeto concreto criado a partir da classe.

```python
class ContaBancaria:
    def __init__(self, titular, saldo=0):
        self.titular = titular
        self.saldo = saldo

    def depositar(self, valor):
        self.saldo += valor
```

`__init__` é o inicializador, chamado quando você escreve `conta = ContaBancaria("Ana")`. O primeiro parâmetro de todo método é `self`, a referência ao próprio objeto; é por ele que os atributos são lidos e gravados. Chamar `conta.depositar(100)` é o mesmo que `ContaBancaria.depositar(conta, 100)`.

A herança permite que uma classe reaproveite atributos e métodos de outra e os estenda: `class ContaPoupanca(ContaBancaria):`. A classe filha pode sobrescrever métodos da mãe e chamar a versão original com `super()`, por exemplo `super().__init__(titular, saldo)` dentro do seu próprio `__init__`. Use herança quando existe de fato uma relação "é um"; para reutilizar comportamento sem essa relação, a composição (guardar um objeto dentro do outro) costuma ser mais flexível.

Métodos especiais, com dois sublinhados, integram o objeto à linguagem: `__str__` define o texto mostrado pelo `print`, `__repr__` a representação para depuração, `__eq__` a comparação com `==`, `__len__` o resultado de `len`. Com `@property` um método é acessado como atributo, útil para valores calculados ou validados.

Atributos de classe são compartilhados por todas as instâncias; atributos definidos em `self` pertencem a cada objeto. Por convenção, um sublinhado inicial (`_saldo`) indica "uso interno"; o Python não impede o acesso, apenas sinaliza a intenção.

Para classes que servem principalmente para guardar dados, o decorador `@dataclass` gera `__init__`, `__repr__` e `__eq__` automaticamente a partir das anotações de tipo:

```python
@dataclass
class Livro:
    titulo: str
    autor: str
    ano: int
```

Com `frozen=True` as instâncias viram imutáveis. Dataclasses reduzem código repetitivo e deixam a intenção clara, e são uma boa primeira escolha para modelos simples.
