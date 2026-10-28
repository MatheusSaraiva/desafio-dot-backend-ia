# Prova: Desenvolvedor Backend com foco em IA

Solução das três questões da prova técnica, em Python 3.13:

| Questão | O que pede | Onde está | Como rodar |
|---|---|---|---|
| 1. API de biblioteca virtual | Cadastro e consulta de livros por título/autor, SQLite, testes, documentação | [`api_biblioteca/`](api_biblioteca/) (Django + DRF) | `make run-api` → http://127.0.0.1:8000/api/docs/ |
| 2. Chatbot com IA generativa | Perguntas sobre Python via LangChain + OpenAI, exemplos | [`chatbot_python/`](chatbot_python/) | `make chat` |
| 3. Busca semântica | Embeddings + FAISS, função de busca, exemplos | [`busca_semantica/`](busca_semantica/) | `make build-index` e `make search Q="..."` |

Testes das três questões: `make test` (offline, sem chaves).

_(README em construção: as seções detalhadas de cada questão, decisões e exemplos entram ao final da implementação.)_
