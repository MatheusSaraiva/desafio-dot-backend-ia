# Exemplos de busca semântica (Questão 3)

Gerado em 2026-10-29 com `uv run python -m busca_semantica.exemplos`. Modelo `intfloat/multilingual-e5-small` (dimensão 384), 51 chunks de 22 documentos (chunks de até 1200 caracteres).

## Consultas de exemplo (top 3 por documento, busca semântica)

### “como criar uma lista e adicionar itens”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.895 | Listas em Python: criando e manipulando coleções ordenadas (`listas`) | A lista é a estrutura de dados mais usada em Python. Ela guarda uma sequência ordenada de itens, aceita itens de tipos diferentes e pode crescer ou encolher a qualquer momento. Para criar uma lista, use colchetes:… |
| 2 | 0.865 | List comprehension: construindo listas de forma compacta (`list-comprehension`) | A list comprehension é uma sintaxe para criar uma lista nova a partir de uma sequência existente, em uma única expressão. O padrão tradicional com laço e `append` fica assim: ```python quadrados = [] for n in range(10):… |
| 3 | 0.861 | Tuplas e imutabilidade: quando usar uma tupla em vez de uma lista (`tuplas-e-imutabilidade`) | Para acessar elementos, use o índice como na lista: `ponto[0]`. Fatiamento, `len`, `in` e o laço `for` também funcionam. Os únicos métodos disponíveis são `count` e `index`, justamente porque nada que altere a tupla faz… |

### “percorrer os elementos de uma coleção”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.850 | Decoradores: adicionando comportamento a funções sem alterar seu código (`decoradores`) | Dois cuidados: mantenha os decoradores simples e previsíveis, porque eles escondem comportamento de quem lê apenas a função decorada; e lembre-se de que a ordem importa quando há vários empilhados: o decorador mais… |
| 2 | 0.850 | Conjuntos (set): elementos únicos e operações de teoria dos conjuntos (`conjuntos`) | Um conjunto (`set`) é uma coleção sem ordem e sem elementos repetidos. Ele é criado com chaves ou com `set()`: `tags = {"python", "backend", "api"}`. Atenção: `{}` cria um dicionário vazio, então um conjunto vazio é… |
| 3 | 0.847 | Listas em Python: criando e manipulando coleções ordenadas (`listas`) | Ordenar é simples: `frutas.sort()` ordena a própria lista, enquanto `sorted(frutas)` devolve uma nova lista ordenada e deixa a original intacta. Os dois aceitam `reverse=True` e o parâmetro `key`, que recebe uma função… |

### “o que acontece quando o programa encontra um erro”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.879 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Quando algo dá errado em tempo de execução, o Python levanta uma exceção: dividir por zero gera `ZeroDivisionError`, acessar uma chave inexistente gera `KeyError`, converter "abc" para inteiro gera `ValueError`, abrir… |
| 2 | 0.855 | Decoradores: adicionando comportamento a funções sem alterar seu código (`decoradores`) | Um decorador é uma função que recebe outra função e devolve uma versão "embrulhada" dela, com algum comportamento extra antes ou depois. A sintaxe com `@` é só açúcar: escrever `@medir_tempo` acima de `def processar()`… |
| 3 | 0.852 | Funções: definição, parâmetros, valores padrão e retorno (`funcoes`) | Para aceitar uma quantidade variável de argumentos, use `*args` (tupla com os posicionais extras) e `**kwargs` (dicionário com os nomeados extras). Isso é comum em funções que repassam argumentos para outras. As… |

### “isolar as dependências de cada projeto”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.868 | Módulos, pacotes e ambientes virtuais: organizando e instalando dependências (`modulos-pacotes-e-ambientes`) | A solução é o ambiente virtual: uma instalação isolada do Python por projeto. Crie com `python -m venv .venv`, ative com `source .venv/bin/activate` (Linux e macOS) ou `.venv\Scripts\activate` (Windows) e instale as… |
| 2 | 0.856 | Decoradores: adicionando comportamento a funções sem alterar seu código (`decoradores`) | Dois cuidados: mantenha os decoradores simples e previsíveis, porque eles escondem comportamento de quem lê apenas a função decorada; e lembre-se de que a ordem importa quando há vários empilhados: o decorador mais… |
| 3 | 0.849 | LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos (`lgpd-e-ia-em-treinamentos`) | Em soluções white label, em que a mesma plataforma atende várias empresas, o isolamento entre clientes (multi-tenant) é um requisito de arquitetura, não um detalhe: a base de conhecimento de uma organização nunca pode… |

### “economizar memória ao processar um arquivo gigante”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.873 | Arquivos: ler e escrever texto, CSV e JSON (`arquivos`) | Para abrir um arquivo, use `open` dentro de um bloco `with`. O `with` garante que o arquivo é fechado ao final, mesmo que aconteça um erro no meio: ```python with open("notas.txt", encoding="utf-8") as arquivo: conteudo… |
| 2 | 0.862 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e,… |
| 3 | 0.853 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Quando algo dá errado em tempo de execução, o Python levanta uma exceção: dividir por zero gera `ZeroDivisionError`, acessar uma chave inexistente gera `KeyError`, converter "abc" para inteiro gera `ValueError`, abrir… |

### “como funciona um tutor de IA que responde com base no material do curso”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.891 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | Quando escala, a IA deve entregar contexto ao tutor: o histórico da conversa, o que já foi tentado e o motivo do encaminhamento. E deve dizer ao aluno o que vai acontecer e em quanto tempo, em vez de simplesmente parar… |
| 2 | 0.858 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | As vantagens são concretas. O conhecimento fica atualizado sem retreinar o modelo: basta reindexar os documentos. As respostas podem citar de onde vieram, o que permite ao usuário conferir. E a instrução "responda… |
| 3 | 0.852 | LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos (`lgpd-e-ia-em-treinamentos`) | Plataformas de aprendizagem guardam dados pessoais: nome, cargo, desempenho em avaliações, conversas com tutores e, com assistentes de IA, o conteúdo das perguntas dos alunos. A Lei Geral de Proteção de Dados (LGPD)… |

### “quando o robô deve chamar um humano”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.841 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | O objetivo nunca é substituir o tutor, e sim multiplicar seu alcance: menos tempo respondendo "onde está o PDF" e mais tempo acompanhando quem está com dificuldade de verdade. |
| 2 | 0.824 | O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações (`o-que-e-rag`) | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e,… |
| 3 | 0.813 | Decoradores: adicionando comportamento a funções sem alterar seu código (`decoradores`) | Dois cuidados: mantenha os decoradores simples e previsíveis, porque eles escondem comportamento de quem lê apenas a função decorada; e lembre-se de que a ordem importa quando há vários empilhados: o decorador mais… |

### “proteção de dados pessoais na plataforma de ensino”

| # | Cosseno | Documento | Trecho que casou |
|---|---|---|---|
| 1 | 0.896 | LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos (`lgpd-e-ia-em-treinamentos`) | Plataformas de aprendizagem guardam dados pessoais: nome, cargo, desempenho em avaliações, conversas com tutores e, com assistentes de IA, o conteúdo das perguntas dos alunos. A Lei Geral de Proteção de Dados (LGPD)… |
| 2 | 0.831 | Exceções: tratando erros com try, except, else e finally (`excecoes`) | Para sinalizar um erro no seu próprio código, use `raise`: `raise ValueError("A data de publicação não pode estar no futuro.")`. Crie exceções próprias herdando de `Exception` quando quiser que quem chama consiga… |
| 3 | 0.831 | Tutoria com IA e mediação humana: quando o chatbot deve escalar para uma pessoa (`tutoria-ia-e-mediacao-humana`) | Em operações de aprendizagem com milhares de alunos, a maior parte das dúvidas é repetitiva: onde encontro o material, como emito o certificado, o que significa determinado conceito da aula 3. Um assistente de IA… |

## O que o chatbot recebe da base (busca híbrida, 4 melhores chunks)

O RAG da Questão 2 pede chunks, não documentos: um artigo dividido em duas partes pode ter a resposta na segunda. Abaixo, cada linha é um chunk (`documento #parte`), com o filtro `score_minimo = 0.837` aplicado no lado semântico.

### “O que é RAG e por que reduz alucinações?”

| # | RRF | Chunk | Começo do trecho |
|---|---|---|---|
| 1 | 0.033 | `o-que-e-rag #1` | As vantagens são concretas. O conhecimento fica atualizado sem retreinar o modelo: basta reindexar os documentos. As… |
| 2 | 0.032 | `o-que-e-rag #0` | Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma… |
| 3 | 0.016 | `lgpd-e-ia-em-treinamentos #2` | Transparência com o aluno fecha o ciclo: informar que há uma IA na conversa, para que os dados são usados e como pedir… |

### “Quando um chatbot de tutoria deve passar a dúvida para uma pessoa?”

| # | RRF | Chunk | Começo do trecho |
|---|---|---|---|
| 1 | 0.032 | `tutoria-ia-e-mediacao-humana #0` | Em operações de aprendizagem com milhares de alunos, a maior parte das dúvidas é repetitiva: onde encontro o material,… |
| 2 | 0.032 | `tutoria-ia-e-mediacao-humana #2` | O objetivo nunca é substituir o tutor, e sim multiplicar seu alcance: menos tempo respondendo "onde está o PDF" e mais… |
| 3 | 0.032 | `tutoria-ia-e-mediacao-humana #1` | Quando escala, a IA deve entregar contexto ao tutor: o histórico da conversa, o que já foi tentado e o motivo do… |
| 4 | 0.016 | `microlearning-no-whatsapp #1` | Há cuidados de desenho. O conteúdo precisa ser pensado para o formato, e não ser um curso longo picado: cada pílula tem… |

### “receita de bolo de cenoura”

Nenhum chunk acima do limiar: a base não cobre o assunto e o chatbot é avisado.

## Limiar de relevância

O FAISS sempre devolve vizinhos, mesmo para uma pergunta que a base não cobre. O limiar é escolhido olhando o cosseno do 1º resultado em dois grupos:

| Grupo | Consulta | Cosseno do 1º resultado |
|---|---|---|
| com resposta na base (pior das 22) | coleção que não pode ser alterada depois de criada | 0.844 |
| fora do domínio | receita de bolo de cenoura | 0.820 |
| fora do domínio | qual a capital da França | 0.788 |
| fora do domínio | como trocar o pneu do carro | 0.813 |
| fora do domínio | previsão do tempo para amanhã em Florianópolis | 0.819 |
| fora do domínio | melhor time de futebol do Brasil | 0.795 |
| fora do domínio | sintomas de gripe e o que tomar | 0.831 |

`score_minimo = 0.837` separa os dois grupos (domínio ≥ 0.844, fora ≤ 0.831). A margem é pequena, como se espera de um modelo small: um reranker seria o próximo passo.

## Avaliação: 22 consultas com resposta conhecida (k=3)

As consultas foram escritas como paráfrases, com pouca sobreposição de palavras com os documentos, para medir compreensão de significado e não casamento de termos.

| Método | recall@1 | recall@3 | MRR@3 |
|---|---|---|---|
| Semântica (e5 + FAISS) | 0.77 | 0.91 | 0.841 |
| BM25 (lexical) | 0.77 | 0.95 | 0.856 |
| Híbrida (RRF) | 0.95 | 1.00 | 0.977 |

| Consulta | Documento esperado | Semântica | BM25 | Híbrida |
|---|---|---|---|---|
| como guardar vários valores em sequência e acrescentar novos no final | `listas` | fora do top 3 | 3 | 2 |
| coleção que não pode ser alterada depois de criada | `tuplas-e-imutabilidade` | fora do top 3 | 1 | 1 |
| estrutura para associar uma chave a um valor | `dicionarios` | 1 | 1 | 1 |
| eliminar repetidos de uma coleção | `conjuntos` | 1 | 1 | 1 |
| repetir um bloco de código para cada elemento | `loops-for-while` | 1 | fora do top 3 | 1 |
| como definir parâmetros opcionais com valor padrão | `funcoes` | 1 | 1 | 1 |
| gerar uma lista nova a partir de outra em uma única linha | `list-comprehension` | 2 | 2 | 1 |
| inserir o valor de uma variável dentro de um texto | `strings-e-fstrings` | 1 | 1 | 1 |
| ler o conteúdo de um csv linha por linha | `arquivos` | 1 | 1 | 1 |
| o que fazer quando o programa quebra com um erro | `excecoes` | 1 | 1 | 1 |
| reaproveitar atributos e métodos de outra classe | `classes-e-objetos` | 1 | 1 | 1 |
| instalar bibliotecas sem bagunçar o sistema | `modulos-pacotes-e-ambientes` | 1 | 1 | 1 |
| produzir valores um por vez sem carregar tudo na memória | `geradores-e-iteradores` | 1 | 2 | 1 |
| adicionar comportamento a uma função sem mexer no corpo dela | `decoradores` | 1 | 1 | 1 |
| indicar que um parâmetro deve ser inteiro | `type-hints` | 2 | 2 | 1 |
| verificar automaticamente se o código continua funcionando | `testes-com-pytest` | 2 | 1 | 1 |
| fazer o modelo de linguagem responder com base em documentos da empresa | `o-que-e-rag` | 1 | 1 | 1 |
| quando a IA deve passar a dúvida do aluno para uma pessoa | `tutoria-ia-e-mediacao-humana` | 1 | 1 | 1 |
| treinamento em pílulas curtas pelo celular | `microlearning-no-whatsapp` | 1 | 1 | 1 |
| como saber se o curso trouxe resultado para a empresa | `metricas-de-treinamento` | 1 | 1 | 1 |
| representar o significado de um texto como números | `embeddings-e-busca-semantica` | 1 | 1 | 1 |
| cuidados com dados pessoais dos alunos ao usar IA | `lgpd-e-ia-em-treinamentos` | 1 | 1 | 1 |
