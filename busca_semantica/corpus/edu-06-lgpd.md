---
title: LGPD e IA em treinamentos corporativos: cuidados com os dados dos alunos
slug: lgpd-e-ia-em-treinamentos
tags: educação corporativa, lgpd, privacidade, inteligência artificial
source: artigo original escrito para este corpus
---
Plataformas de aprendizagem guardam dados pessoais: nome, cargo, desempenho em avaliações, conversas com tutores e, com assistentes de IA, o conteúdo das perguntas dos alunos. A Lei Geral de Proteção de Dados (LGPD) exige que esses dados sejam tratados com finalidade definida, base legal, transparência e segurança, e dá ao titular direitos como acesso, correção e exclusão.

Quando um assistente de IA entra na plataforma, alguns cuidados se tornam concretos. Minimização: envie ao modelo de linguagem apenas o necessário para responder; não há motivo para incluir CPF, matrícula ou histórico completo do aluno no prompt. Anonimização e pseudonimização nos registros de conversa, principalmente nos que servem para analisar padrões de dúvidas. Retenção definida: conversas e logs têm prazo para serem apagados.

Em soluções white label, em que a mesma plataforma atende várias empresas, o isolamento entre clientes (multi-tenant) é um requisito de arquitetura, não um detalhe: a base de conhecimento de uma organização nunca pode ser recuperada em uma consulta feita por outra. Isso se traduz em filtros obrigatórios por tenant em toda busca vetorial, chaves e índices separados quando o risco justificar, e testes automatizados que tentam vazar dados entre clientes.

O uso de provedores externos de LLM também precisa de contrato e configuração adequados: onde os dados são processados, se são usados para treinar modelos do provedor (deve estar desabilitado), por quanto tempo ficam armazenados e quem responde em caso de incidente. Registrar essas escolhas facilita a resposta a auditorias e a questionários de segurança dos clientes.

Transparência com o aluno fecha o ciclo: informar que há uma IA na conversa, para que os dados são usados e como pedir exclusão. Guardrails no assistente evitam que ele colete dados sensíveis sem necessidade ou responda sobre temas fora do escopo do curso. E o princípio de "privacidade desde o desenho" vale para o pipeline de RAG inteiro: do que entra na ingestão ao que aparece nos logs de observabilidade.

Tratar a LGPD como parte do produto, e não como obstáculo, costuma ser um diferencial comercial: grandes empresas e o setor público perguntam sobre isso antes de perguntar sobre a qualidade das respostas.
