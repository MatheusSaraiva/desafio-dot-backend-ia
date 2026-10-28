---
title: Embeddings e busca semântica: como vetores representam o significado de um texto
slug: embeddings-e-busca-semantica
tags: inteligência artificial, embeddings, busca semântica
source: artigo original escrito para este corpus
---
A busca tradicional por palavras-chave encontra documentos que contêm exatamente os termos digitados. Se o aluno pergunta "como emitir o comprovante" e o manual fala em "certificado", a busca lexical falha. A busca semântica resolve isso representando textos por significado, e não por palavras.

A representação é o embedding: um vetor de números (centenas de dimensões) produzido por um modelo de linguagem treinado para que textos com significado parecido fiquem próximos no espaço vetorial. "Comprovante de conclusão" e "certificado do curso" geram vetores vizinhos; "certificado" e "receita de bolo" ficam longe. A proximidade é medida pela similaridade de cosseno, que compara a direção dos vetores e vai de -1 a 1 (quanto maior, mais parecido).

Para buscar, o sistema calcula o embedding de cada trecho dos documentos uma única vez e guarda em um índice vetorial. Na consulta, calcula o embedding da pergunta e procura os vetores mais próximos. Bibliotecas como FAISS fazem essa busca de forma muito eficiente; para volumes grandes, usam índices aproximados (como HNSW) que trocam um pouco de precisão por velocidade. Bancos como Milvus e OpenSearch oferecem a mesma capacidade como serviço, com filtros por metadados e escala horizontal.

Alguns detalhes práticos fazem diferença. Documentos longos são divididos em chunks, porque o modelo tem um limite de tokens e porque um vetor de um texto muito longo "dilui" os assuntos. Incluir o título no texto de cada chunk ajuda o vetor a carregar o contexto. Modelos multilíngues, como a família multilingual-e5 ou o bge-m3, funcionam bem em português; alguns pedem prefixos diferentes para consulta e documento. E o mesmo modelo que indexou precisa ser o que consulta, porque vetores de modelos diferentes não são comparáveis.

A busca semântica não substitui totalmente a lexical: nomes próprios, códigos de produto e siglas ainda são mais bem encontrados por correspondência exata. Por isso sistemas de produção costumam ser híbridos, combinando os dois rankings. E, como todo componente de recuperação, ela deve ser medida com consultas de teste e respostas conhecidas, acompanhando métricas como recall@k e MRR a cada mudança de modelo ou de chunking.
