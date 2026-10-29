# Prova: Desenvolvedor Backend com foco em IA

[![CI](https://github.com/MatheusSaraiva/desafio-dot-backend-ia/actions/workflows/ci.yml/badge.svg)](https://github.com/MatheusSaraiva/desafio-dot-backend-ia/actions/workflows/ci.yml)

Solução das três questões da prova, em Python 3.13, num único repositório:

| Questão | O que pede | Onde está | Como rodar |
|---|---|---|---|
| **1. API de biblioteca virtual** | Cadastro e consulta de livros por título/autor, SQLite, testes, endpoints documentados | [`api_biblioteca/`](api_biblioteca/) (Django + DRF) | `make run-api` → http://127.0.0.1:8000/api/docs/ |
| **2. Chatbot com IA generativa** | Perguntas sobre Python via LangChain + OpenAI, com exemplos | [`chatbot_python/`](chatbot_python/) (LangChain v1, LangSmith) | `make chat` |
| **3. Busca semântica** | Embeddings + vector store, função de busca, exemplos | [`busca_semantica/`](busca_semantica/) (sentence-transformers + FAISS) | `make build-index` e `make search Q="..."` |

Os testes das três questões rodam offline, sem chave de API e sem baixar modelos: `make test` (85 testes).
Exemplos reais: [`docs/exemplos_q2.md`](docs/exemplos_q2.md) (conversas com o chatbot) e [`docs/exemplos_q3.md`](docs/exemplos_q3.md) (buscas, o que o RAG recebe, limiar de relevância e avaliação).

## Setup (5 comandos)

Pré-requisito: [`uv`](https://docs.astral.sh/uv/) (instala o Python 3.13 sozinho se faltar).

```bash
git clone https://github.com/MatheusSaraiva/desafio-dot-backend-ia.git && cd desafio-dot-backend-ia
make setup            # uv sync (torch só CPU, ~200 MB) + cria .env a partir do .env.example
make test             # 85 testes, offline
make seed && make run-api                       # Questão 1 em http://127.0.0.1:8000/api/docs/
make build-index && make search Q="como percorrer uma lista"   # Questão 3 (baixa o e5-small, ~470 MB, 1 vez)
```

Para a Questão 2, preencha `OPENAI_API_KEY` no `.env` (e, opcionalmente, `LANGSMITH_API_KEY` + `LANGSMITH_TRACING=true`) e rode `make chat`. Para usar a DeepSeek no lugar da OpenAI, preencha `DEEPSEEK_API_KEY` e defina `LLM_MODEL=deepseek:deepseek-flash`.

Sem `make`: os comandos equivalentes estão no [`Makefile`](Makefile) (todos são `uv run ...`).

## Questão 1: API de biblioteca (Django + DRF)

Escolhi Django + DRF porque é o framework pedido como preferência nas dicas da prova e o que entrega mais com menos código neste escopo: ORM com SQLite sem configuração, migrations, admin, validação em serializers e documentação OpenAPI gerada do código com `drf-spectacular`.

**Endpoints** (base `/api/livros/`, documentação interativa em `/api/docs/`, schema em `/api/schema/`):

| Método e rota | O que faz |
|---|---|
| `POST /api/livros/` | Cadastra um livro (`titulo`, `autor`, `data_publicacao`, `resumo`) |
| `GET /api/livros/?titulo=cortico` | Consulta por título (parcial; ignora acentos e maiúsculas: acha "O Cortiço") |
| `GET /api/livros/?autor=machado` | Consulta por autor (idem; os dois filtros podem ser combinados) |
| `GET /api/livros/?q=alencar` | Busca livre em título **e** autor |
| `GET /api/livros/?ano=1899&ordering=titulo` | Filtros extras (ano, `publicado_apos`, `publicado_antes`) e ordenação |
| `GET /api/livros/{id}/` | Detalhe; `PUT`/`PATCH`/`DELETE` para manutenção |

Listagens são paginadas (20 por página; `?page_size=` até 100). Validações: campos obrigatórios e não vazios, data de publicação não pode estar no futuro, datas no formato `AAAA-MM-DD`, e o mesmo livro (título + autor + data, ignorando acentos e caixa) não entra duas vezes (400 com mensagem; há também uma `UniqueConstraint` no banco).

**Busca sem acentos.** O `LIKE` do SQLite só ignora maiúsculas em ASCII: `icontains` não acharia "O Cortiço" com `cortico` nem "Aluísio" com `ALUÍSIO`. Por isso o modelo guarda `titulo_normalizado` e `autor_normalizado` (sem acentos, `casefold`), preenchidos por um signal `pre_save` (cobre também o `loaddata` da fixture), e os filtros normalizam o termo digitado do mesmo jeito. Em Postgres isso seria `unaccent` + `citext`; aqui a coluna derivada é a solução portátil.

```bash
curl -X POST http://127.0.0.1:8000/api/livros/ -H "Content-Type: application/json" \
  -d '{"titulo": "Dom Casmurro", "autor": "Machado de Assis", "data_publicacao": "1899-01-01", "resumo": "Bento Santiago relembra Capitu."}'
curl "http://127.0.0.1:8000/api/livros/?autor=machado"
```

Código: modelo em [`livros/models.py`](api_biblioteca/livros/models.py), validações em [`livros/serializers.py`](api_biblioteca/livros/serializers.py), filtros em [`livros/filters.py`](api_biblioteca/livros/filters.py), endpoints em [`livros/views.py`](api_biblioteca/livros/views.py). Fixture com 10 livros em `livros/fixtures/livros.json` (`make seed`; as datas dos clássicos usam 1º de janeiro do ano de publicação). Testes: [`tests/test_q1_api.py`](tests/test_q1_api.py) (36 testes com pytest-django, banco temporário por teste: cadastro, validações, duplicatas, consultas com e sem acento, paginação, manutenção, fixture e schema).

## Questão 2: chatbot de Python (LangChain v1 + OpenAI + LangSmith)

```bash
make chat                                                   # conversa no terminal, com streaming
uv run python -m chatbot_python.cli --pergunta "Como criar uma lista em Python?"
uv run python -m chatbot_python.cli --rag                   # usa a busca semântica da Questão 3 como ferramenta
uv run python -m chatbot_python.cli --model deepseek:deepseek-flash   # outro provedor, mesma conversa
```

**Como funciona** ([`chatbot_python/agent.py`](chatbot_python/agent.py)):

- O agente é montado com `create_agent` da API v1 do LangChain, com um modelo de chat criado por `init_chat_model` a partir de `LLM_MODEL` (`provedor:modelo`), um system prompt de tutor de Python em português ([`prompts.py`](chatbot_python/prompts.py)) e memória de conversa por `thread_id` (checkpointer do LangGraph). "E como adiciono um item **nela**?" funciona porque o histórico da thread vai junto.
- **Provedores**: OpenAI é o padrão (é o que o enunciado pede); a DeepSeek entra como opção pelo pacote oficial `langchain-deepseek`, sem mudar código: `LLM_MODEL=deepseek:deepseek-flash` + `DEEPSEEK_API_KEY` (testado: o `deepseek-flash` responde e chama as ferramentas, inclusive o RAG com citação de fonte). Só a chave do provedor escolhido é obrigatória; se faltar a chave de um e existir a do outro, a mensagem de erro diz como trocar. A tabela `PROVEDORES` em [`settings.py`](chatbot_python/settings.py) é o único lugar a tocar para adicionar outro (Anthropic, Gemini).
- **Ferramentas** ([`tools.py`](chatbot_python/tools.py)): `consultar_base_conhecimento` (RAG sobre os artigos da Questão 3, com busca híbrida; o prompt pede para citar as fontes) e `encaminhar_para_tutor` (simula o handoff para um tutor humano, o modelo de mediação híbrida IA + pessoas). Sem ferramentas, é um chatbot puro; com elas, um agente ReAct.
- **RAG que recebe trechos, não documentos.** A tool pede os 4 melhores *chunks* (`agrupar_por_documento=False`), porque a resposta pode estar na segunda parte de um artigo: na primeira versão, que agrupava por documento, o chunk com a definição de RAG era o 2º melhor do índice e nem chegava ao modelo, que respondia "a base não trouxe a definição". Há um limiar de relevância (`score_minimo`, calibrado na Questão 3): para "receita de bolo" a tool devolve "nenhum trecho relevante" em vez de três trechos irrelevantes, e o modelo é instruído a dizer que não achou fonte. O score não vai para o modelo (o da busca híbrida é RRF, não similaridade).
- **LangSmith**: com `LANGSMITH_TRACING=true` e a chave no `.env`, cada pergunta vira um trace (função `perguntar` decorada com `@traceable`, com as chamadas ao modelo e às ferramentas aninhadas, latência e tokens). Sem chave válida o tracing é desligado no processo, para o SDK não tentar enviar e imprimir `403` a cada pergunta.
- **Custo e robustez**: `max_tokens`, `timeout`, `max_retries` e quantidade de trechos do RAG configuráveis ([`settings.py`](chatbot_python/settings.py)), limite de tamanho da pergunta (validado antes de carregar modelo e índice), tokens de entrada/saída reportados em cada resposta (também no streaming), erros da API traduzidos em uma linha (sem traceback com variáveis locais, que poderia vazar a chave). O "GPT-4" do enunciado é legado; o padrão é o `openai:gpt-5.4-mini` (US$ 0,75/4,50 por 1M tokens) e a geração atual (`openai:gpt-6.1-terra`, `openai:gpt-6-luna`) funciona trocando só a variável.
- **Exemplos**: [`docs/exemplos_q2.md`](docs/exemplos_q2.md), gerado por `uv run python -m chatbot_python.exemplos` com respostas reais e contagem de tokens (duas conversas: memória/escopo e RAG/encaminhamento). Foram gerados com `deepseek:deepseek-flash`, o provedor para o qual eu tinha chave no momento; o comando é o mesmo para a OpenAI, trocando `LLM_MODEL`.

Testes ([`tests/test_q2_chatbot.py`](tests/test_q2_chatbot.py)): o modelo é substituído por um `GenericFakeChatModel` roteirizado, então os testes cobrem memória por thread, ferramentas (incluindo o RAG de verdade sobre o corpus: trechos de um mesmo artigo, aviso quando nada passa do limiar), validações, configuração (chaves, placeholder do `.env.example`, tracing) e o CLI, sem chave nem custo. Um teste de integração real contra o provedor configurado fica atrás do marcador `integration` (`uv run pytest -m integration`).

## Questão 3: busca semântica (sentence-transformers + FAISS)

```bash
make build-index                                    # corpus -> chunks -> embeddings -> índice FAISS em busca_semantica/index/
make search Q="economizar memória ao processar um arquivo gigante"
uv run python -m busca_semantica.cli search "quando o robô deve chamar um humano" --modo hibrida
uv run python -m busca_semantica.cli search "o que é RAG" --modo hibrida --por-chunk   # como o chatbot vê
uv run python -m busca_semantica.cli search "receita de bolo" --score-minimo 0.837    # fora do domínio: vazio
make evaluate                                       # recall@1, recall@3, MRR e calibração do limiar
```

**Pipeline** (um módulo por etapa, documentado no código):

1. [`ingest.py`](busca_semantica/ingest.py): lê o corpus (22 artigos originais em português em [`corpus/`](busca_semantica/corpus/): 16 sobre Python, que o chatbot consome, e 6 sobre educação corporativa com IA) e divide em chunks de até 1200 caracteres com overlap de 150 (`RecursiveCharacterTextSplitter`). O título do artigo entra no texto de cada chunk. O tamanho foi escolhido pelo limite do modelo: o e5 lê 512 tokens e trunca o resto em silêncio; com 1200 caracteres o maior chunk fica em 413 tokens, e `build-index` imprime esse número para quem trocar o corpus ou o modelo.
2. [`embeddings.py`](busca_semantica/embeddings.py): `intfloat/multilingual-e5-small` via sentence-transformers, vetores normalizados, prefixos `query:`/`passage:` que a família e5 exige. Há um `FakeEmbedder` determinístico para os testes.
3. [`store.py`](busca_semantica/store.py): FAISS `IndexFlatIP` (produto interno de vetores normalizados = similaridade de cosseno; busca exata, adequada até centenas de milhares de vetores). Índice, chunks e metadados são persistidos em disco.
4. [`search.py`](busca_semantica/search.py): `buscar(consulta, k)` devolve os resultados mais relevantes com score e trecho. Agrupando por documento (padrão, o que uma pessoa espera de uma busca) o melhor chunk representa cada artigo; sem agrupar, vêm os k melhores chunks (o que o RAG precisa). Um `score_minimo` opcional corta o que fica abaixo do limiar: o FAISS sempre devolve k vizinhos, mesmo para "receita de bolo", e é o limiar que separa "parecido" de "irrelevante".
5. [`lexical.py`](busca_semantica/lexical.py) e [`hybrid.py`](busca_semantica/hybrid.py): baseline lexical BM25 sobre os mesmos chunks e busca híbrida por Reciprocal Rank Fusion (por documento ou por chunk). Se nada passa do limiar semântico, a híbrida devolve vazio mesmo que o BM25 tenha algum termo em comum.
6. [`evaluate.py`](busca_semantica/evaluate.py): 22 consultas com resposta conhecida, escritas como paráfrases (pouca sobreposição de palavras), medidas em recall@k e MRR; e a calibração do limiar, comparando o cosseno do 1º resultado dessas consultas com o de 6 consultas fora do domínio.

**Resultado medido** (22 consultas, k=3, detalhes em [`docs/exemplos_q3.md`](docs/exemplos_q3.md)):

| Método | recall@1 | recall@3 | MRR@3 |
|---|---|---|---|
| Semântica (e5-small + FAISS) | 0,77 | 0,91 | 0,841 |
| BM25 (lexical) | 0,77 | 0,95 | 0,856 |
| **Híbrida (RRF)** | **0,95** | **1,00** | **0,977** |

Os erros são complementares: a semântica confunde documentos vizinhos (listas, list comprehension, tuplas) e o BM25 falha quando a consulta não repete palavras do documento ("verificar automaticamente se o código continua funcionando" → artigo de pytest). A fusão corrige os dois lados, por isso o chatbot usa a híbrida. Troquei o modelo por `multilingual-e5-base` para medir (`build-index --model intfloat/multilingual-e5-base --index-dir busca_semantica/index_e5base` e `evaluate --index-dir ...`): semântica 0,86 / 0,95 / 0,909 e híbrida 0,91 / 1,00 / 0,955. Mantive o `small` como padrão pelo tempo de setup (470 MB vs 1,1 GB); em produção a escolha seria guiada por essa mesma avaliação sobre consultas reais.

**Limiar de relevância.** Com o e5-small, a pior consulta com resposta na base dá cosseno 0,844 e a melhor consulta fora do domínio ("sintomas de gripe") dá 0,831; `score_minimo = 0,837` é o ponto médio. A margem é estreita, como se espera de um modelo small (as similaridades ficam comprimidas entre 0,78 e 0,90), e o valor é específico do modelo: com o e5-base a escala muda e `make evaluate --index-dir busca_semantica/index_e5base` avisa que o limiar precisa ser recalibrado. O próximo passo natural seria um reranker cross-encoder, que separa muito melhor os dois grupos.

Testes ([`tests/test_q3_busca.py`](tests/test_q3_busca.py)): pipeline completo com o embedder simulado (ingestão, chunking, índice, persistência, busca por documento e por chunk, limiar, avaliação, calibração, BM25, híbrida) e um teste com o modelo real atrás do marcador `slow`.

## Decisões e trade-offs

| Decisão | Por quê | Alternativa considerada |
|---|---|---|
| Um repositório, um `pyproject.toml`, três pacotes | As questões conversam entre si (o chatbot usa a busca); um só `make test` e um só CI | Três repositórios (mais atrito para avaliar) |
| Django + DRF na Q1 | Preferência indicada na prova; SQLite e docs OpenAPI com configuração mínima | FastAPI + SQLModel (igualmente bom; menos "de graça" para CRUD + admin) |
| LangChain v1 (`create_agent`) na Q2 | API atual; chains legadas (`LLMChain`, `ConversationChain`) foram para `langchain-classic` | LangGraph puro (mais controle, mais código para o mesmo resultado) |
| OpenAI como padrão, DeepSeek como opção (`init_chat_model`) | É o que o enunciado pede; `gpt-5.4-mini` custa centavos por conversa. A DeepSeek entra pelo pacote oficial do LangChain, com a mesma interface e os mesmos controles de custo | Trocar a OpenAI por outro provedor como padrão (foge do enunciado) |
| Testes com LLM e embedder simulados | Rodam em segundos, sem chave e sem rede, no CI | Só testes de integração (lentos, caros, não determinísticos) |
| FAISS `IndexFlatIP` | Exato e sem treino; o corpus é pequeno | IVF/HNSW (aproximados, só valem para milhões de vetores); Milvus (serviço a mais para um teste) |
| `multilingual-e5-small` | Bom em português, leve em CPU; avaliação mostrou o ganho do `base` | `bge-m3` (2 GB, 8k tokens), embeddings da OpenAI (custo por chamada e dependência externa) |
| Busca híbrida (RRF) no RAG, por chunk, com limiar | Mediu melhor que semântica e BM25 isolados; por chunk porque a resposta pode estar na 2ª parte do artigo; o limiar evita entregar trechos irrelevantes ao modelo | Reranker cross-encoder (próximo passo natural) |
| Colunas normalizadas para a busca da Q1 | O SQLite não ignora acentos; a coluna derivada funciona em qualquer banco | `unaccent` do Postgres (prende ao banco), normalizar em Python a cada consulta (não usa índice) |
| torch fixado na build CPU | A wheel padrão para Linux puxa bibliotecas CUDA (vários GB) | Deixar o padrão (instalação de 5 GB para quem avalia) |

## Como isso evoluiria em produção

Pensando na stack descrita na vaga (Django, MongoDB, OpenSearch, Celery, LangChain):

- **Ingestão assíncrona** com Celery: upload do documento → task de chunking + embeddings → indexação, com retry e idempotência; reindexação incremental quando o conteúdo muda.
- **OpenSearch** no lugar do FAISS: índice k-NN para os vetores e BM25 nativo, com a busca híbrida feita no próprio motor, filtros por metadados e, essencial numa solução white label, **filtro obrigatório por tenant** em toda consulta (isolamento entre clientes, LGPD).
- **MongoDB** para conversas, checkpoints do agente (trocando o `InMemorySaver` por um checkpointer persistente) e configuração por cliente (prompt, base de conhecimento, modelo).
- **Qualidade contínua**: o conjunto de consultas com resposta conhecida vira um dataset no LangSmith; cada mudança de modelo, chunking ou prompt é avaliada antes de ir para produção (recall/MRR na recuperação, grounding e utilidade na resposta).
- **Mediação híbrida de verdade**: o `encaminhar_para_tutor` vira um ticket na fila dos tutores, com o histórico anexado e SLA; métricas de resolução na primeira camada e de escalonamento.
- **Canais**: a mesma API de pergunta/resposta atrás do LMS (LTI) e do WhatsApp, com FastAPI para serviços leves e MCP para expor ferramentas (catálogo de cursos, progresso do aluno) aos agentes.

## Limitações conhecidas

- O corpus é pequeno e foi escrito por mim; as 22 consultas de avaliação e as 6 fora do domínio também. Os números servem para comparar métodos entre si, não como medida absoluta de qualidade, e o limiar de relevância tem margem estreita (0,831 vs 0,844).
- A API da Questão 1 é pública (sem autenticação), como cabe no escopo da prova; em produção entraria JWT/SSO.
- A memória do chatbot vive no processo (`InMemorySaver`): reiniciar o CLI zera as conversas.
- O encaminhamento para tutor é um stub em memória que prova o fluxo do agente; não há fila real.
- `make build-index` baixa o modelo de embeddings da HuggingFace na primeira execução (precisa de internet).

## Processo de desenvolvimento

Usei um assistente de código com IA (Claude Code) como par de programação, no espírito de "codificação assistida" citado na vaga: ele acelerou a escrita de código repetitivo, testes e documentação; as decisões de arquitetura, a escolha das bibliotecas e versões (verificadas no PyPI e na documentação oficial do LangChain v1), a revisão de cada arquivo e a validação (lint, 85 testes, execução real de ponta a ponta) foram minhas. Depois da primeira versão, uma revisão crítica com a solução rodando de verdade levou às correções do RAG (trechos em vez de documentos, limiar de relevância), da busca sem acentos na API e do tamanho dos chunks. O histórico de commits mostra a ordem em que as coisas foram construídas. Comentários no código explicam o porquê das escolhas, como pedido no enunciado.

Qualidade: `ruff` (lint + formatação) e `pytest` rodam no CI (GitHub Actions) a cada push, sem chaves externas.
