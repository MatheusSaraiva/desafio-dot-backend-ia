# Exemplos de perguntas e respostas (Questão 2)

Gerado em 2026-10-29 com `deepseek:deepseek-flash` via `uv run python -m chatbot_python.exemplos`. Respostas reais, sem edição.


## Conversa 1: memória e escopo

Opções: `{'com_tutor': False}` · thread `conversa-1-mem-ria-e-escopo`

**Você:** Como criar uma lista em Python?

**Tutor:**

Uma lista é uma sequência ordenada e mutável de valores, criada com colchetes `[]` (ou com `list()`). Ela aceita qualquer tipo de elemento, inclusive tipos misturados.

```python
frutas = ["maçã", "banana", "uva"]   # lista literal
vazia = []                            # lista vazia
numeros = list(range(3))              # a partir de um iterável -> [0, 1, 2]

print(frutas[0])      # maçã  (índice começa em 0)
print(len(frutas))    # 3
frutas.append("pera") # adiciona no final
print(frutas)         # ['maçã', 'banana', 'uva', 'pera']
```

Erros comuns:

- **Acessar índice inexistente**: `frutas[3]` dá `IndexError`. Use `frutas[-1]` para o último item.
- **Confundir lista com tupla**: `(1, 2)` é uma tupla, imutável — não dá para fazer `append` nela.

<sub>tokens: 337 entrada + 288 saída · ferramentas: nenhuma</sub>

---

**Você:** E como adiciono um item nela?

**Tutor:**

"Dela" = a lista `frutas` do exemplo anterior. Você tem algumas formas, dependendo de **onde** quer adicionar:

```python
frutas = ["maçã", "banana", "uva"]

frutas.append("pera")        # no final -> ['maçã', 'banana', 'uva', 'pera']
frutas.insert(1, "kiwi")     # em posição específica -> ['maçã', 'kiwi', 'banana', 'uva', 'pera']
frutas.extend(["manga", "caju"])  # vários itens de uma vez, no final
frutas += ["abacaxi"]        # equivalente a extend
print(frutas)
```

Diferença importante entre `append` e `extend`:

```python
a = [1, 2]
a.append([3, 4])   # vira [1, 2, [3, 4]]  -> adiciona a lista como UM item
a = [1, 2]
a.extend([3, 4])   # vira [1, 2, 3, 4]    -> adiciona cada elemento
```

Erros comuns:

- **Usar `append` quando queria `extend`**: gera listas aninhadas sem querer (como no exemplo acima).
- **Esperar retorno**: `append`, `insert` e `extend` alteram a lista no lugar e retornam `None`. Ou seja, `frutas = frutas.append("pera")` deixa `frutas` como `None` — não faça isso.

<sub>tokens: 607 entrada + 397 saída · ferramentas: nenhuma</sub>

---

**Você:** Qual a diferença entre lista e tupla?

**Tutor:**

A diferença central é a **mutabilidade**: lista (`[]`) pode ser alterada depois de criada; tupla (`()`) é imutável. Tudo o mais (indexação, fatiamento, `len`, `in`, iteração) funciona igual nas duas.

```python
lista = [1, 2, 3]
lista[0] = 99        # ok
lista.append(4)      # ok

tupla = (1, 2, 3)
tupla[0] = 99        # TypeError: 'tuple' object does not support item assignment
```

Consequências práticas:

```python
# 1) Tupla pode ser chave de dict / elemento de set (se os itens forem hashable)
coordenadas = (10, 20)
pontos = {coordenadas: "origem"}     # ok
# {[10, 20]: "origem"}               # TypeError: unhashable type: 'list'

# 2) Desempacotamento e retorno de funções
def minmax(nums):
    return min(nums), max(nums)      # retorna uma tupla

lo, hi = minmax([3, 1, 7])

# 3) Tupla de um elemento precisa da vírgula
t = (5)      # isso é só o int 5
t = (5,)     # isso é uma tupla
```

Quando usar cada uma:

- **Lista**: coleção homogênea que vai crescer/encolher — `["a", "b"]`, resultados de um loop.
- **Tupla**: registro de tamanho fixo com significados posicionais — `(x, y)`, `(nome, idade)` — ou quando precisa de hash/constância.

Erros comuns:

- **Achar que tupla é "lista mais rápida"**: a diferença de performance existe, mas é pequena; escolha por semântica, não por micro-otimização.
- **Esquecer a vírgula** em tupla de um elemento: `(5)` é `int`, `(5,)` é `tuple`.

<sub>tokens: 981 entrada + 553 saída · ferramentas: nenhuma</sub>

---

**Você:** Como leio um arquivo CSV e somo uma coluna?

**Tutor:**

O jeito mais direto com a biblioteca padrão é `csv.DictReader`: ele usa a primeira linha como cabeçalho e entrega cada linha como dicionário, então você acessa a coluna pelo nome. O ponto de atenção é que **o CSV entrega tudo como string** — é preciso converter para `float` antes de somar.

Imaginando um `vendas.csv`:

```
produto,preco,quantidade
caneta,2.50,10
caderno,15.90,3
borracha,1.20,5
```

```python
import csv

total = 0.0
with open("vendas.csv", newline="", encoding="utf-8") as f:
    leitor = csv.DictReader(f)
    for linha in leitor:
        valor = linha["preco"].strip()
        if valor:                      # ignora campos vazios
            total += float(valor.replace(",", "."))  # se usar vírgula decimal

print(f"Total: {total:.2f}")
```

Se preferir pandas (instale com `pip install pandas`), fica em duas linhas — e o pandas já converte tipos:

```python
import pandas as pd

df = pd.read_csv("vendas.csv", decimal=",")  # decimal="," se o CSV usar vírgula
print(df["preco"].sum())
```

Erros comuns:

- **Somar strings**: `sum(linha["preco"] for ...)` sem `float()` falha ou concatena. Sempre converta antes.
- **Esquecer `newline=""`** no `open`: em arquivos com campos multilinha ou no Windows isso pode gerar linhas em branco/duplicadas. A documentação do `csv` recomenda explicitamente.
- **Separador errado**: se o arquivo usa `;` (comum no Brasil), passe `delimiter=";"` no `csv.reader`/`DictReader` ou `sep=";"` no pandas. Sem isso tudo vem em uma coluna só.
- **Encoding**: arquivos do Excel podem vir em `latin-1` ou com BOM (`utf-8-sig`). Se der `UnicodeDecodeError` ou o primeiro nome de coluna vier estranho, é por aí.

Se quiser, me diga o formato exato do seu CSV (separador e nome da coluna) que eu ajusto o código.

<sub>tokens: 1469 entrada + 659 saída · ferramentas: nenhuma</sub>

---

**Você:** O que é list comprehension e quando não devo usar?

**Tutor:**

List comprehension é uma forma compacta de construir uma lista a partir de um iterável, juntando o `for` (e opcionalmente um `if`) dentro dos colchetes. O resultado é uma **nova** lista, sem precisar de `append`.

```python
# forma "tradicional"
quadrados = []
for n in range(5):
    quadrados.append(n * n)

# list comprehension equivalente
quadrados = [n * n for n in range(5)]        # [0, 1, 4, 9, 16]

# com filtro
pares = [n for n in range(10) if n % 2 == 0] # [0, 2, 4, 6, 8]
```

A leitura correta é: *"para cada `n` em `range(5)` que satisfaz o `if`, produza `n * n`"*. Note que a ordem é `expressão → for → if`, mas mentalmente você lê `for → if → expressão`.

### Quando **não** usar

- **Quando você só quer o efeito colateral, não a lista.** Se não vai guardar o resultado, use um `for` normal. `[print(x) for x in itens]` cria uma lista inútil e confunde quem lê.
- **Quando fica difícil ler.** Se precisa de mais de um `for` aninhado, ou de um `if`/`else` complexo, um loop explícito costuma ser mais claro — e o Python tem um guia de estilo (PEP 8) dizendo para priorizar legibilidade.
- **Quando a lógica tem várias etapas ou tratamento de erro.** `try/except` dentro de comprehension é feio; use um loop.
- **Quando a sequência é enorme e você não precisa de todos os itens de uma vez.** Aí um *generator expression* com parênteses evita materializar tudo na memória:

```python
soma = sum(n * n for n in range(10_000_000))  # parênteses: gera sob demanda
```

### Pegadinhas comuns

- **`if/else` tem ordem diferente**: o `else` vem logo após a expressão, não no final.
```python
rotulos = ["par" if n % 2 == 0 else "ímpar" for n in range(4)]
```
- **Sobrescrever variável que você ia usar depois**: a variável do `for` "vaza" para o escopo em Python 3? Não — ela fica local; mas cuidado ao reutilizar o mesmo nome de uma variável externa, o valor antigo se perde.
- **Achar que comprehension é sempre mais rápida**: costuma ser um pouco, mas só quando você realmente quer a lista. Para efeito colateral, é desperdício.
- **Lista de listas com `[[0] * 3] * 3`**: isso é outro tema (aliasing), mas é um erro clássico de quem vem de syntactic sugar — as linhas ficam compartilhadas.

<sub>tokens: 2026 entrada + 727 saída · ferramentas: nenhuma</sub>

---

**Você:** Me dá uma receita de bolo de cenoura?

**Tutor:**

Essa eu vou ficar devendo 🙂 — meu foco é Python e seu ecossistema, então não sou a melhor fonte para receitas.

Mas se quiser, posso ajudar com algo relacionado, por exemplo:

- um script em Python que converte unidades de medida de receitas (xícaras ↔ ml, °C ↔ °F);
- uma estrutura de dados (dict, dataclass ou até um JSON) para guardar ingredientes e quantidades;
- uma função de escalonamento que ajusta uma receita para N porções.

Quer seguir por algum desses caminhos, ou tem outra dúvida de Python?

<sub>tokens: 2728 entrada + 165 saída · ferramentas: nenhuma</sub>

---

Total da conversa: 10937 tokens.


## Conversa 2: RAG e encaminhamento

Opções: `{'com_rag': True}` · thread `conversa-2-rag-e-encaminhamento`

**Você:** O que é RAG e por que reduz alucinações?

**Tutor:**

## O que é RAG

RAG (Retrieval-Augmented Generation, ou geração aumentada por recuperação) é uma arquitetura que faz o modelo responder com base em **documentos seus**, não só no que ele aprendeu no treinamento. Funciona em duas etapas:

1. **Recuperação**: a pergunta do usuário é usada para buscar os trechos mais relevantes numa base de documentos da organização.
2. **Geração**: esses trechos entram no prompt junto com a pergunta, e o modelo é instruído a responder só com base neles, citando a fonte.

Antes disso existe um pipeline de ingestão: os textos são cortados em pedaços (*chunks*), cada pedaço vira um vetor numérico via modelo de *embeddings*, e os vetores ficam num índice vetorial (FAISS, Milvus, OpenSearch...). Na hora da pergunta, ela também vira vetor, e os pedaços mais próximos são recuperados por similaridade semântica.

## Por que reduz alucinações

O modelo deixa de depender da memória paramétrica ("o que eu lembro do treino") e passa a ter o texto relevante na frente dele, no próprio contexto. Some-se a isso uma instrução explícita do tipo *"responda apenas com base no contexto; se não estiver no contexto, diga que não sabe"* — e a taxa de invenção cai bastante. Como as respostas citam a origem, o usuário também pode conferir.

Exemplo mínimo da etapa de recuperação:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

chunks = [
    "A política de reembolso aceita solicitações em até 30 dias.",
    "O curso de Python tem 40 horas e certificado ao final.",
    "Férias devem ser solicitadas com 15 dias de antecedência.",
]

# indexação: cada chunk vira um vetor
vetores = model.encode(chunks, normalize_embeddings=True)

def buscar(pergunta: str, k: int = 2) -> list[str]:
    v = model.encode([pergunta], normalize_embeddings=True)[0]
    similaridades = vetores @ v          # produto escalar = similaridade de cosseno
    melhores = np.argsort(similaridades)[::-1][:k]
    return [chunks[i] for i in melhores]

print(buscar("quantas horas tem o curso de python?"))
```

O `@` faz o produto escalar; como os vetores estão normalizados, o resultado equivale à similaridade de cosseno. Os trechos retornados seriam colocados no prompt do LLM.

**Erros comuns:**

- **Achar que RAG é mágica.** A qualidade depende da recuperação. *Chunks* mal cortados, documentos desatualizados ou um modelo de *embeddings* fraco no português entregam respostas ruins mesmo com um ótimo LLM. Times maduros medem recall@k e MRR, usam *reranking* e busca híbrida (semântica + palavras-chave).
- **Confiar só no prompt.** Sem avaliar se a resposta está de fato apoiada nos trechos recuperados (*grounding*), você troca uma alucinação por outra — agora com uma citação que parece legítima.

Se você estiver pensando em montar isso na prática (FAISS, Chroma, LangChain), posso detalhar a parte de ingestão ou de avaliação — é só dizer.

Fontes:
- O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações

<sub>tokens: 2989 entrada + 1131 saída · ferramentas: consultar_base_conhecimento</sub>

---

**Você:** Quando um chatbot de tutoria deve passar a dúvida para uma pessoa?

**Tutor:**

## O modelo: mediação híbrida

A recomendação é a **mediação híbrida**: a IA é a primeira camada, o tutor humano a segunda. A maior parte das dúvidas é repetitiva ("onde acho o PDF", "como emito o certificado", "o que significa X da aula 3") e a IA resolve em segundos, a qualquer hora, liberando o tutor para o que exige julgamento pedagógico. O objetivo não é substituir o tutor, e sim multiplicar o alcance dele.

A decisão de escalar precisa ser **explícita e baseada em critérios**, não no acaso. Os gatilhos típicos:

| Gatilho | Exemplo |
|---|---|
| O aluno pede uma pessoa | "queria falar com um professor" |
| Envolve avaliação, nota ou prazo | "minha nota na atividade 2 está errada", "posso entregar depois?" |
| Falta base documental | a busca não retorna nada acima do limiar de similaridade |
| Frustração ou repetição | aluno reclamando, ou repetindo a mesma pergunta |
| Tema sensível | saúde, assédio, situação pessoal |

Um esboço de como isso vira código:

```python
GATILHOS_SENSIVEIS = {"nota", "avaliação", "prazo", "recurso", "assédio", "saúde"}

def deve_escalar(pergunta: str, chunks: list[str], score: float,
                 tentativas: int, frustrado: bool) -> tuple[bool, str]:
    p = pergunta.lower()

    if any(t in p for t in ("falar com", "atendente", "humano", "tutor")):
        return True, "aluno pediu atendimento humano"
    if any(t in p for t in GATILHOS_SENSIVEIS):
        return True, "tema que exige decisão do tutor (nota/prazo/sensível)"
    if not chunks or score < 0.35:
        return True, "sem base documental suficiente"
    if tentativas >= 2 or frustrado:
        return True, "aluno repetiu a pergunta ou demonstrou frustração"
    return False, ""
```

O limiar `0.35` é ilustrativo — calibre com dados reais das suas perguntas sem resposta.

## O que fazer *depois* de escalar

Dois pontos que costumam ser esquecidos:

1. **Entregue contexto ao tutor**: histórico da conversa, o que a IA já tentou e o motivo do encaminhamento. Sem isso o aluno repete tudo e a experiência fica pior do que se nunca tivesse falado com a IA.
2. **Avise o aluno**: diga o que vai acontecer e em quanto tempo — *"vou encaminhar sua dúvida para a tutora, que responde em até 24 horas úteis"* — em vez de simplesmente parar de responder.

**Erro comum:** olhar só a taxa de escalonamento como se menor fosse melhor. Muito baixa pode significar que a IA está respondendo o que não deveria (inclusive nota e prazo); muito alta, que a base de conhecimento está incompleta. O par saudável é acompanhar taxa de escalonamento **junto** com taxa de resolução na primeira camada e satisfação em cada camada.

Se quiser, posso te mostrar como registrar esses eventos para medir os indicadores.

Fontes:
- Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa
- O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações

<sub>tokens: 6565 entrada + 973 saída · ferramentas: consultar_base_conhecimento</sub>

---

**Você:** Quero falar com um tutor humano sobre a nota da minha prova.

**Tutor:**

Pronto, encaminhei sua solicitação (ticket #1). Um tutor humano vai responder em **até 24 horas úteis** sobre a nota da sua prova.

Para agilizar o atendimento dele, vale já ter em mãos: o nome da disciplina, qual avaliação é e, se possível, o que você esperava da correção — assim ele consegue verificar direto no sistema.

Enquanto isso, continuo à disposição para qualquer dúvida de Python — de sintaxe a bibliotecas, testes, boas práticas. Só lembrando que questões de nota, prazo e avaliação ficam com a tutoria humana.

<sub>tokens: 9517 entrada + 294 saída · ferramentas: encaminhar_para_tutor</sub>

---

Total da conversa: 21469 tokens.


Total geral: 32406 tokens.
