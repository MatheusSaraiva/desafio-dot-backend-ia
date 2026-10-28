---
title: O que é RAG (Retrieval-Augmented Generation) e por que ele reduz alucinações
slug: o-que-e-rag
tags: inteligência artificial, llm, rag
source: artigo original escrito para este corpus
---
Modelos de linguagem como o GPT respondem a partir do que aprenderam no treinamento. Isso traz dois problemas para uma empresa: o modelo não conhece os documentos internos (políticas, manuais, conteúdo dos cursos) e, quando não sabe, tende a inventar uma resposta plausível, o que chamamos de alucinação.

RAG, sigla de Retrieval-Augmented Generation (geração aumentada por recuperação), resolve isso em duas etapas. Primeiro, a recuperação: a pergunta do usuário é usada para buscar os trechos mais relevantes em uma base de documentos da própria organização. Segundo, a geração: esses trechos são colocados no prompt, junto com a pergunta, e o modelo é instruído a responder com base neles, citando a fonte.

A base de documentos é preparada antes, em um pipeline de ingestão: os textos são divididos em pedaços (chunks), cada pedaço é transformado em um vetor numérico por um modelo de embeddings e os vetores são guardados em um índice vetorial (FAISS, Milvus, OpenSearch). Na hora da pergunta, ela também vira um vetor, e os pedaços mais próximos são recuperados por similaridade semântica.

As vantagens são concretas. O conhecimento fica atualizado sem retreinar o modelo: basta reindexar os documentos. As respostas podem citar de onde vieram, o que permite ao usuário conferir. E a instrução "responda apenas com base no contexto; se não estiver no contexto, diga que não sabe" reduz drasticamente as alucinações.

RAG não é mágica. A qualidade depende da qualidade da recuperação: chunks mal cortados, documentos desatualizados ou um modelo de embeddings fraco no idioma levam a respostas ruins mesmo com um ótimo LLM. Por isso times maduros medem a recuperação separadamente (recall@k, MRR), usam reranking para refinar os candidatos, combinam busca semântica com busca por palavras-chave (busca híbrida) e avaliam continuamente se a resposta está de fato apoiada nos trechos recuperados (grounding).

Em educação corporativa, RAG é o que permite um tutor de IA responder sobre o conteúdo específico de um curso, uma política de RH ou um procedimento operacional da empresa, com fontes, em vez de respostas genéricas da internet.
