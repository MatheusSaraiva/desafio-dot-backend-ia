# Prova: Desenvolvedor Backend com foco em IA

[![CI](https://github.com/MatheusSaraiva/desafio-dot-backend-ia/actions/workflows/ci.yml/badge.svg)](https://github.com/MatheusSaraiva/desafio-dot-backend-ia/actions/workflows/ci.yml)

Solução das três questões da prova, em Python 3.13, num único repositório:

| Questão | O que pede | Onde está | Como rodar |
|---|---|---|---|
| **1. API de biblioteca virtual** | Cadastro e consulta de livros por título/autor, SQLite, testes, endpoints documentados | [`api_biblioteca/`](api_biblioteca/) (Django + DRF) | `make run-api` → http://127.0.0.1:8000/api/docs/ |
| **2. Chatbot com IA generativa** | Perguntas sobre Python via LangChain + OpenAI, com exemplos | [`chatbot_python/`](chatbot_python/) (LangChain v1, LangSmith) | `make chat` |
| **3. Busca semântica** | Embeddings + vector store, função de busca, exemplos | [`busca_semantica/`](busca_semantica/) (sentence-transformers + FAISS) | `make build-index` e `make search Q="..."` |

Os testes das três questões rodam offline, sem chave de API e sem baixar modelos: `make test` (50 testes).
Exemplos reais: [`docs/exemplos_q2.md`](docs/exemplos_q2.md) (conversas com o chatbot) e [`docs/exemplos_q3.md`](docs/exemplos_q3.md) (buscas e avaliação).

## Setup (5 comandos)

Pré-requisito: [`uv`](https://docs.astral.sh/uv/) (instala o Python 3.13 sozinho se faltar).

```bash
git clone https://github.com/MatheusSaraiva/desafio-dot-backend-ia.git && cd desafio-dot-backend-ia
make setup            # uv sync (torch só CPU, ~200 MB) + cria .env a partir do .env.example
make test             # 50 testes, offline
make seed && make run-api                       # Questão 1 em http://127.0.0.1:8000/api/docs/
make build-index && make search Q="como percorrer uma lista"   # Questão 3 (baixa o e5-small, ~470 MB, 1 vez)
```

Para a Questão 2, preencha `OPENAI_API_KEY` no `.env` (e, opcionalmente, `LANGSMITH_API_KEY` + `LANGSMITH_TRACING=true`) e rode `make chat`.

Sem `make`: os comandos equivalentes estão no [`Makefile`](Makefile) (todos são `uv run ...`).

## Questão 1: API de biblioteca (Django + DRF)

Escolhi Django + DRF porque é o framework pedido como preferência nas dicas da prova e o que entrega mais com menos código neste escopo: ORM com SQLite sem configuração, migrations, admin, validação em serializers e documentação OpenAPI gerada do código com `drf-spectacular`.

**Endpoints** (base `/api/livros/`, documentação interativa em `/api/docs/`, schema em `/api/schema/`):

| Método e rota | O que faz |
|---|---|
| `POST /api/livros/` | Cadastra um livro (`titulo`, `autor`, `data_publicacao`, `resumo`) |
| `GET /api/livros/?titulo=casmurro` | Consulta por título (parcial, sem distinguir maiúsculas) |
| `GET /api/livros/?autor=machado` | Consulta por autor (idem; os dois filtros podem ser combinados) |
| `GET /api/livros/?q=alencar` | Busca livre em título **e** autor |
| `GET /api/livros/?ano=1899&ordering=titulo` | Filtros extras (ano, `publicado_apos`, `publicado_antes`) e ordenação |
| `GET /api/livros/{id}/` | Detalhe; `PUT`/`PATCH`/`DELETE` para manutenção |

Listagens são paginadas (20 por página). Validações: campos obrigatórios e não vazios, data de publicação não pode estar no futuro, datas no formato `AAAA-MM-DD`.

```bash
curl -X POST http://127.0.0.1:8000/api/livros/ -H "Content-Type: application/json" \
  -d '{"titulo": "Dom Casmurro", "autor": "Machado de Assis", "data_publicacao": "1899-01-01", "resumo": "Bento Santiago relembra Capitu."}'
curl "http://127.0.0.1:8000/api/livros/?autor=machado"
```

Código: modelo em [`livros/models.py`](api_biblioteca/livros/models.py), validações em [`livros/serializers.py`](api_biblioteca/livros/serializers.py), filtros em [`livros/filters.py`](api_biblioteca/livros/filters.py), endpoints em [`livros/views.py`](api_biblioteca/livros/views.py). Fixture com 10 livros em `livros/fixtures/livros.json` (`make seed`; as datas dos clássicos usam 1º de janeiro do ano de publicação). Testes: [`tests/test_q1_api.py`](tests/test_q1_api.py) (23 testes com pytest-django, banco temporário por teste).

## Questão 2: chatbot de Python (LangChain v1 + OpenAI + LangSmith)

```bash
make chat                                                   # conversa no terminal, com streaming
uv run python -m chatbot_python.cli --pergunta "Como criar uma lista em Python?"
uv run python -m chatbot_python.cli --rag                   # usa a busca semântica da Questão 3 como ferramenta
```

**Como funciona** ([`chatbot_python/agent.py`](chatbot_python/agent.py)):

- O agente é montado com `create_agent` da API v1 do LangChain, com o modelo da OpenAI (`ChatOpenAI`), um system prompt de tutor de Python em português ([`prompts.py`](chatbot_python/prompts.py)) e memória de conversa por `thread_id` (checkpointer do LangGraph). "E como adiciono um item **nela**?" funciona porque o histórico da thread vai junto.
- **Ferramentas** ([`tools.py`](chatbot_python/tools.py)): `consultar_base_conhecimento` (RAG sobre os artigos da Questão 3, com busca híbrida; o prompt pede para citar as fontes) e `encaminhar_para_tutor` (simula o handoff para um tutor humano, o modelo de mediação híbrida IA + pessoas). Sem ferramentas, é um chatbot puro; com elas, um agente ReAct.
- **LangSmith**: com `LANGSMITH_TRACING=true` e a chave no `.env`, cada pergunta vira um trace (função `perguntar` decorada com `@traceable`, com as chamadas ao modelo e às ferramentas aninhadas). Prints em [`docs/`](docs/).
- **Custo e robustez**: `max_tokens`, `timeout` e `max_retries` configuráveis ([`settings.py`](chatbot_python/settings.py)), limite de tamanho da pergunta, modelo barato por padrão (`gpt-5.4-mini`; o "GPT-4" do enunciado é legado e o modelo é configurável por `OPENAI_MODEL`), tokens de entrada/saída reportados em cada resposta.
- **Exemplos**: [`docs/exemplos_q2.md`](docs/exemplos_q2.md), gerado por `uv run python -m chatbot_python.exemplos` com respostas reais e contagem de tokens (duas conversas: memória/escopo e RAG/encaminhamento).

Testes ([`tests/test_q2_chatbot.py`](tests/test_q2_chatbot.py)): o modelo é substituído por um `GenericFakeChatModel` roteirizado, então os testes cobrem memória por thread, ferramentas (incluindo o RAG de verdade sobre o corpus), validações e métricas sem chave nem custo. Um teste de integração real fica atrás do marcador `integration` (`uv run pytest -m integration`).

## Questão 3: busca semântica (sentence-transformers + FAISS)

```bash
make build-index                                    # corpus -> chunks -> embeddings -> índice FAISS em busca_semantica/index/
make search Q="economizar memória ao processar um arquivo gigante"
uv run python -m busca_semantica.cli search "quando o robô deve chamar um humano" --modo hibrida
make evaluate                                       # recall@1, recall@3, MRR: semântica vs BM25 vs híbrida
```

**Pipeline** (um módulo por etapa, documentado no código):

1. [`ingest.py`](busca_semantica/ingest.py): lê o corpus (22 artigos originais em português em [`corpus/`](busca_semantica/corpus/): 16 sobre Python, que o chatbot consome, e 6 sobre educação corporativa com IA) e divide em chunks de ~1500 caracteres com overlap de 150 (`RecursiveCharacterTextSplitter`). O título do artigo entra no texto de cada chunk.
2. [`embeddings.py`](busca_semantica/embeddings.py): `intfloat/multilingual-e5-small` via sentence-transformers, vetores normalizados, prefixos `query:`/`passage:` que a família e5 exige. Há um `FakeEmbedder` determinístico para os testes.
3. [`store.py`](busca_semantica/store.py): FAISS `IndexFlatIP` (produto interno de vetores normalizados = similaridade de cosseno; busca exata, adequada até centenas de milhares de vetores). Índice, chunks e metadados são persistidos em disco.
4. [`search.py`](busca_semantica/search.py): `buscar(consulta, k)` devolve os documentos mais relevantes, agrupados por documento (o melhor chunk representa cada um), com score e trecho.
5. [`evaluate.py`](busca_semantica/evaluate.py) e [`hybrid.py`](busca_semantica/hybrid.py): 22 consultas com resposta conhecida, escritas como paráfrases (pouca sobreposição de palavras), medidas em recall@k e MRR; baseline lexical BM25 e busca híbrida por Reciprocal Rank Fusion.

**Resultado medido** (22 consultas, k=3, detalhes em [`docs/exemplos_q3.md`](docs/exemplos_q3.md)):

| Método | recall@1 | recall@3 | MRR@3 |
|---|---|---|---|
| Semântica (e5-small + FAISS) | 0,77 | 0,91 | 0,833 |
| BM25 (lexical) | 0,77 | 0,95 | 0,856 |
| **Híbrida (RRF)** | **0,91** | **1,00** | **0,955** |

Os erros são complementares: a semântica confunde documentos vizinhos (listas, list comprehension, tuplas) e o BM25 falha quando a consulta não repete palavras do documento ("verificar automaticamente se o código continua funcionando" → artigo de pytest). A fusão corrige os dois lados, por isso o chatbot usa a híbrida. Troquei o modelo por `multilingual-e5-base` para medir (`build-index --model intfloat/multilingual-e5-base --index-dir busca_semantica/index_e5base` e `evaluate --index-dir ...`): semântica 0,82 / 1,00 / 0,894 e híbrida 0,95 / 1,00 / 0,977. Mantive o `small` como padrão pelo tempo de setup (470 MB vs 1,1 GB); em produção a escolha seria guiada por essa mesma avaliação sobre consultas reais.

Testes ([`tests/test_q3_busca.py`](tests/test_q3_busca.py)): pipeline completo com o embedder simulado (ingestão, chunking, índice, persistência, busca, agrupamento, avaliação, híbrida) e um teste com o modelo real atrás do marcador `slow`.

## Decisões e trade-offs

| Decisão | Por quê | Alternativa considerada |
|---|---|---|
| Um repositório, um `pyproject.toml`, três pacotes | As questões conversam entre si (o chatbot usa a busca); um só `make test` e um só CI | Três repositórios (mais atrito para avaliar) |
| Django + DRF na Q1 | Preferência indicada na prova; SQLite e docs OpenAPI com configuração mínima | FastAPI + SQLModel (igualmente bom; menos "de graça" para CRUD + admin) |
| LangChain v1 (`create_agent`) na Q2 | API atual; chains legadas (`LLMChain`, `ConversationChain`) foram para `langchain-classic` | LangGraph puro (mais controle, mais código para o mesmo resultado) |
| OpenAI como provedor, modelo configurável | É o que o enunciado pede; `gpt-5.4-mini` custa centavos por conversa | Trocar por outro provedor (foge do enunciado) |
| Testes com LLM e embedder simulados | Rodam em segundos, sem chave e sem rede, no CI | Só testes de integração (lentos, caros, não determinísticos) |
| FAISS `IndexFlatIP` | Exato e sem treino; o corpus é pequeno | IVF/HNSW (aproximados, só valem para milhões de vetores); Milvus (serviço a mais para um teste) |
| `multilingual-e5-small` | Bom em português, leve em CPU; avaliação mostrou o ganho do `base` | `bge-m3` (2 GB, 8k tokens), embeddings da OpenAI (custo por chamada e dependência externa) |
| Busca híbrida (RRF) no RAG | Mediu melhor que semântica e BM25 isolados | Reranker cross-encoder (próximo passo natural) |
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

- O corpus é pequeno e foi escrito por mim; as 22 consultas de avaliação também. Os números servem para comparar métodos entre si, não como medida absoluta de qualidade.
- A API da Questão 1 é pública (sem autenticação), como cabe no escopo da prova; em produção entraria JWT/SSO.
- A memória do chatbot vive no processo (`InMemorySaver`): reiniciar o CLI zera as conversas.
- O encaminhamento para tutor é um stub em memória que prova o fluxo do agente; não há fila real.
- `make build-index` baixa o modelo de embeddings da HuggingFace na primeira execução (precisa de internet).

## Processo de desenvolvimento

Usei um assistente de código com IA (Claude Code) como par de programação, no espírito de "codificação assistida" citado na vaga: ele acelerou a escrita de código repetitivo, testes e documentação; as decisões de arquitetura, a escolha das bibliotecas e versões (verificadas no PyPI e na documentação oficial do LangChain v1), a revisão de cada arquivo e a validação (lint, 50 testes, execução real de ponta a ponta) foram minhas. O histórico de commits mostra a ordem em que as coisas foram construídas. Comentários no código explicam o porquê das escolhas, como pedido no enunciado.

Qualidade: `ruff` (lint + formatação) e `pytest` rodam no CI (GitHub Actions) a cada push, sem chaves externas.
