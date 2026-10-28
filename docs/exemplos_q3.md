# Exemplos de busca semântica (Questão 3)

Gerado em 2026-10-28 com `uv run python -m busca_semantica.exemplos`. Modelo `intfloat/multilingual-e5-small` (dimensão 384), 44 chunks de 22 documentos.

## Consultas de exemplo (top 3 por documento)

### “como criar uma lista e adicionar itens”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.890 | Listas em Python: criando e manipulando coleções ordenadas (`listas`) | A lista é a estrutura de dados mais usada em Python. Ela guarda uma sequência ordenada de itens, aceita itens de tipos diferentes e pode crescer ou encolher a qualquer momento. Para criar uma lista, use colchetes:… |
| 2 | 0.874 | Laços for e while: percorrendo sequências e repetindo tarefas (`loops-for-while`) | Evite modificar uma lista enquanto a percorre, porque os índices se deslocam e itens são pulados. Percorra uma cópia (`for item in lista[:]`) ou construa uma nova lista com os itens que devem ficar. Se o objetivo do… |
| 3 | 0.866 | List comprehension: construindo listas de forma compacta (`list-comprehension`) | A list comprehension é uma sintaxe para criar uma lista nova a partir de uma sequência existente, em uma única expressão. O padrão tradicional com laço e `append` fica assim: ```python quadrados = [] for n in range(10):… |

### “percorrer os elementos de uma coleção”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.857 | Listas em Python: criando e manipulando coleções ordenadas (`listas`) | Um detalhe importante: a lista é mutável e passada por referência. Se você fizer `copia = frutas`, as duas variáveis apontam para a mesma lista, e alterar uma altera a outra. Para copiar de verdade, use `frutas.copy()`… |
| 2 | 0.853 | Laços for e while: percorrendo sequências e repetindo tarefas (`loops-for-while`) | Evite modificar uma lista enquanto a percorre, porque os índices se deslocam e itens são pulados. Percorra uma cópia (`for item in lista[:]`) ou construa uma nova lista com os itens que devem ficar. Se o objetivo do… |
| 3 | 0.849 | Conjuntos (set): elementos únicos e operações de teoria dos conjuntos (`conjuntos`) | Um conjunto (`set`) é uma coleção sem ordem e sem elementos repetidos. Ele é criado com chaves ou com `set()`: `tags = {"python", "backend", "api"}`. Atenção: `{}` cria um dicionário vazio, então um conjunto vazio é… |

### “o que acontece quando o programa encontra um erro”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.879 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Quando algo dá errado em tempo de execução, o Python levanta uma exceção: dividir por zero gera `ZeroDivisionError`, acessar uma chave inexistente gera `KeyError`, converter "abc" para inteiro gera `ValueError`, abrir… |
| 2 | 0.853 | Decoradores: adicionando comportamento a funções sem alterar seu código (`decoradores`) | Um decorador é uma função que recebe outra função e devolve uma versão "embrulhada" dela, com algum comportamento extra antes ou depois. A sintaxe com `@` é só açúcar: escrever `@medir_tempo` acima de `def processar()`… |
| 3 | 0.845 | Testes automatizados com pytest: escrevendo e organizando testes (`testes-com-pytest`) | Testes automatizados verificam, a cada mudança, que o código continua fazendo o que deveria. O `pytest` é o framework mais usado em Python porque exige pouco: um arquivo cujo nome começa com `test_`, funções que começam… |

### “isolar as dependências de cada projeto”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.866 | Módulos, pacotes e ambientes virtuais: organizando e instalando dependências (`modulos-pacotes-e-ambientes`) | Essa lista pode ser um `requirements.txt` (gerado com `pip freeze > requirements.txt` e instalado com `pip install -r requirements.txt`) ou, no formato moderno, o arquivo `pyproject.toml`, que descreve o projeto, suas… |
| 2 | 0.845 | Testes automatizados com pytest: escrevendo e organizando testes (`testes-com-pytest`) | `@pytest.mark.parametrize` roda o mesmo teste com vários conjuntos de entrada, cada um aparecendo como um caso separado no relatório. Marcadores personalizados como `@pytest.mark.slow` ou `@pytest.mark.integration`… |
| 3 | 0.842 | Laços for e while: percorrendo sequências e repetindo tarefas (`loops-for-while`) | Evite modificar uma lista enquanto a percorre, porque os índices se deslocam e itens são pulados. Percorra uma cópia (`for item in lista[:]`) ou construa uma nova lista com os itens que devem ficar. Se o objetivo do… |

### “economizar memória ao processar um arquivo gigante”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.871 | Arquivos: ler e escrever texto, CSV e JSON (`arquivos`) | Para abrir um arquivo, use `open` dentro de um bloco `with`. O `with` garante que o arquivo é fechado ao final, mesmo que aconteça um erro no meio: ```python with open("notas.txt", encoding="utf-8") as arquivo: conteudo… |
| 2 | 0.862 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e,… |
| 3 | 0.853 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Quando algo dá errado em tempo de execução, o Python levanta uma exceção: dividir por zero gera `ZeroDivisionError`, acessar uma chave inexistente gera `KeyError`, converter "abc" para inteiro gera `ValueError`, abrir… |

### “como funciona um tutor de IA que responde com base no material do curso”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.893 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | Em operações de aprendizagem com milhares de alunos, a maior parte das dúvidas é repetitiva: onde encontro o material, como emito o certificado, o que significa determinado conceito da aula 3. Um assistente de IA… |
| 2 | 0.848 | LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos (`lgpd-e-ia-em-treinamentos`) | Plataformas de aprendizagem guardam dados pessoais: nome, cargo, desempenho em avaliações, conversas com tutores e, com assistentes de IA, o conteúdo das perguntas dos alunos. A Lei Geral de Proteção de Dados (LGPD)… |
| 3 | 0.848 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e,… |

### “quando o robô deve chamar um humano”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.832 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | Em operações de aprendizagem com milhares de alunos, a maior parte das dúvidas é repetitiva: onde encontro o material, como emito o certificado, o que significa determinado conceito da aula 3. Um assistente de IA… |
| 2 | 0.823 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e,… |
| 3 | 0.815 | Dicionários: mapeando chaves a valores (`dicionarios`) | Dois utilitários do módulo `collections` evitam código repetitivo. `defaultdict(list)` cria a lista automaticamente na primeira vez que uma chave é usada, ótimo para agrupar itens. `Counter` conta ocorrências:… |

### “proteção de dados pessoais na plataforma de ensino”

| # | Score | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.878 | LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos (`lgpd-e-ia-em-treinamentos`) | Plataformas de aprendizagem guardam dados pessoais: nome, cargo, desempenho em avaliações, conversas com tutores e, com assistentes de IA, o conteúdo das perguntas dos alunos. A Lei Geral de Proteção de Dados (LGPD)… |
| 2 | 0.831 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | Transparência é obrigatória: o aluno precisa saber que está falando com uma IA. Respostas devem citar o material do curso de onde vieram, para que ele possa aprofundar e para que o tutor consiga auditar. Um bom tutor de… |
| 3 | 0.831 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Para sinalizar um erro no seu próprio código, use `raise`: `raise ValueError("A data de publicação não pode estar no futuro.")`. Crie exceções próprias herdando de `Exception` quando quiser que quem chama consiga… |

## Avaliação: 22 consultas com resposta conhecida (k=3)

As consultas foram escritas como paráfrases, com pouca sobreposição de palavras com os documentos, para medir compreensão de significado e não casamento de termos.

| Método | recall@1 | recall@3 | MRR@3 |
|---|---|---|---|
| Semântica (e5 + FAISS) | 0.77 | 0.91 | 0.833 |
| BM25 (lexical) | 0.77 | 0.95 | 0.856 |
| Híbrida (RRF) | 0.91 | 1.00 | 0.955 |

| Consulta | Documento esperado | Semântica | BM25 | Híbrida |
|---|---|---|---|---|
| como guardar vários valores em sequência e acrescentar novos no final | `listas` | fora do top 3 | 2 | 2 |
| coleção que não pode ser alterada depois de criada | `tuplas-e-imutabilidade` | 3 | 1 | 1 |
| estrutura para associar uma chave a um valor | `dicionarios` | 1 | 1 | 1 |
| eliminar repetidos de uma coleção | `conjuntos` | 2 | 1 | 1 |
| repetir um bloco de código para cada elemento | `loops-for-while` | 1 | 1 | 1 |
| como definir parâmetros opcionais com valor padrão | `funcoes` | 1 | 1 | 1 |
| gerar uma lista nova a partir de outra em uma única linha | `list-comprehension` | fora do top 3 | 2 | 2 |
| inserir o valor de uma variável dentro de um texto | `strings-e-fstrings` | 1 | 1 | 1 |
| ler o conteúdo de um csv linha por linha | `arquivos` | 1 | 1 | 1 |
| o que fazer quando o programa quebra com um erro | `excecoes` | 1 | 1 | 1 |
| reaproveitar atributos e métodos de outra classe | `classes-e-objetos` | 1 | 1 | 1 |
| instalar bibliotecas sem bagunçar o sistema | `modulos-pacotes-e-ambientes` | 1 | 1 | 1 |
| produzir valores um por vez sem carregar tudo na memória | `geradores-e-iteradores` | 1 | 2 | 1 |
| adicionar comportamento a uma função sem mexer no corpo dela | `decoradores` | 1 | 1 | 1 |
| indicar que um parâmetro deve ser inteiro | `type-hints` | 1 | 1 | 1 |
| verificar automaticamente se o código continua funcionando | `testes-com-pytest` | 1 | fora do top 3 | 1 |
| fazer o modelo de linguagem responder com base em documentos da empresa | `o-que-e-rag` | 1 | 1 | 1 |
| quando a IA deve passar a dúvida do aluno para uma pessoa | `tutoria-ia-e-mediacao-humana` | 1 | 1 | 1 |
| treinamento em pílulas curtas pelo celular | `microlearning-no-whatsapp` | 1 | 1 | 1 |
| como saber se o curso trouxe resultado para a empresa | `metricas-de-treinamento` | 1 | 3 | 1 |
| representar o significado de um texto como números | `embeddings-e-busca-semantica` | 2 | 1 | 1 |
| cuidados com dados pessoais dos alunos ao usar IA | `lgpd-e-ia-em-treinamentos` | 1 | 1 | 1 |
