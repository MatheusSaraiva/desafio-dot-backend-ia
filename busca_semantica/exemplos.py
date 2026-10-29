"""Gera o arquivo de exemplos da busca semântica, em Markdown.

    uv run python -m busca_semantica.exemplos > docs/exemplos_q3.md

Usa o índice salvo em disco (rode `make build-index` antes). Carrega o modelo uma única
vez e imprime: consultas de exemplo com os 3 melhores documentos, o que o RAG do chatbot
recebe (chunks), a calibração do limiar de relevância e a avaliação recall@k / MRR
comparada com o baseline BM25 e com a busca híbrida.
"""

from datetime import date

from .config import settings
from .evaluate import CONSULTAS_AVALIACAO, avaliar, calibrar_score_minimo
from .hybrid import BuscadorHibrido
from .lexical import BuscadorBM25
from .search import carregar_buscador

# Consultas escolhidas para mostrar semântica (paráfrases, sinônimos, dois domínios).
CONSULTAS_EXEMPLO = [
    "como criar uma lista e adicionar itens",
    "percorrer os elementos de uma coleção",
    "o que acontece quando o programa encontra um erro",
    "isolar as dependências de cada projeto",
    "economizar memória ao processar um arquivo gigante",
    "como funciona um tutor de IA que responde com base no material do curso",
    "quando o robô deve chamar um humano",
    "proteção de dados pessoais na plataforma de ensino",
]

# Perguntas que o chatbot faz à base (Questão 2): mostra os chunks que ele recebe.
CONSULTAS_RAG = [
    "O que é RAG e por que reduz alucinações?",
    "Quando um chatbot de tutoria deve passar a dúvida para uma pessoa?",
    "receita de bolo de cenoura",
]


def _resumo(texto: str, limite: int = 220) -> str:
    texto = " ".join(texto.split())
    return texto if len(texto) <= limite else texto[:limite].rsplit(" ", 1)[0] + "…"


def main() -> None:
    buscador = carregar_buscador()
    indice = buscador.indice
    bm25 = BuscadorBM25(indice.chunks)
    hibrido = BuscadorHibrido(buscador, bm25)
    print("# Exemplos de busca semântica (Questão 3)\n")
    print(
        f"Gerado em {date.today().isoformat()} com `uv run python -m busca_semantica.exemplos`. "
        f"Modelo `{indice.nome_modelo}` (dimensão {indice.dimensao}), "
        f"{len(indice)} chunks de {len({c.doc_id for c in indice.chunks})} documentos "
        f"(chunks de até {settings.chunk_size} caracteres).\n"
    )

    print("## Consultas de exemplo (top 3 por documento, busca semântica)\n")
    for consulta in CONSULTAS_EXEMPLO:
        print(f"### “{consulta}”\n")
        print("| # | Cosseno | Documento | Trecho que casou |")
        print("|---|---|---|---|")
        for pos, r in enumerate(buscador.buscar(consulta, k=3), start=1):
            print(f"| {pos} | {r.score:.3f} | {r.titulo} (`{r.doc_id}`) | {_resumo(r.trecho)} |")
        print()

    print("## O que o chatbot recebe da base (busca híbrida, 4 melhores chunks)\n")
    print(
        "O RAG da Questão 2 pede chunks, não documentos: um artigo dividido em duas partes "
        "pode ter a resposta na segunda. Abaixo, cada linha é um chunk (`documento #parte`), "
        f"com o filtro `score_minimo = {settings.score_minimo}` aplicado no lado semântico.\n"
    )
    com_limiar = carregar_buscador(embedder=buscador.embedder, score_minimo=settings.score_minimo)
    rag = BuscadorHibrido(com_limiar, bm25)
    for consulta in CONSULTAS_RAG:
        resultados = rag.buscar(consulta, k=4, agrupar_por_documento=False)
        print(f"### “{consulta}”\n")
        if not resultados:
            print(
                "Nenhum chunk acima do limiar: a base não cobre o assunto e o chatbot é avisado.\n"
            )
            continue
        print("| # | RRF | Chunk | Começo do trecho |")
        print("|---|---|---|---|")
        for pos, r in enumerate(resultados, start=1):
            chunk = f"`{r.doc_id} #{r.indice_chunk}`"
            print(f"| {pos} | {r.score:.3f} | {chunk} | {_resumo(r.trecho, 120)} |")
        print()

    print("## Limiar de relevância\n")
    calibracao = calibrar_score_minimo(buscador, score_minimo=settings.score_minimo)
    print(
        "O FAISS sempre devolve vizinhos, mesmo para uma pergunta que a base não cobre. "
        "O limiar é escolhido olhando o cosseno do 1º resultado em dois grupos:\n"
    )
    print("| Grupo | Consulta | Cosseno do 1º resultado |")
    print("|---|---|---|")
    pior = min(calibracao.no_dominio, key=lambda item: item[1])
    grupo = f"com resposta na base (pior das {len(calibracao.no_dominio)})"
    print(f"| {grupo} | {pior[0]} | {pior[1]:.3f} |")
    for consulta, score in calibracao.fora_do_dominio:
        print(f"| fora do domínio | {consulta} | {score:.3f} |")
    veredito = "separa" if calibracao.separa else "não separa"
    faixa = (
        f"domínio ≥ {calibracao.menor_no_dominio:.3f}, "
        f"fora ≤ {calibracao.maior_fora_do_dominio:.3f}"
    )
    print(
        f"\n`score_minimo = {settings.score_minimo}` {veredito} os dois grupos ({faixa}). "
        "A margem é pequena, como se espera de um modelo small: um reranker seria o próximo "
        "passo.\n"
    )

    k = 3
    metodos = {
        "Semântica (e5 + FAISS)": avaliar(buscador, CONSULTAS_AVALIACAO, k=k),
        "BM25 (lexical)": avaliar(bm25, CONSULTAS_AVALIACAO, k=k),
        "Híbrida (RRF)": avaliar(hibrido, CONSULTAS_AVALIACAO, k=k),
    }

    print(f"## Avaliação: {len(CONSULTAS_AVALIACAO)} consultas com resposta conhecida (k={k})\n")
    print(
        "As consultas foram escritas como paráfrases, com pouca sobreposição de palavras "
        "com os documentos, para medir compreensão de significado e não casamento de termos.\n"
    )
    print(f"| Método | recall@1 | recall@{k} | MRR@{k} |")
    print("|---|---|---|---|")
    for nome, m in metodos.items():
        print(f"| {nome} | {m.recall_at_1:.2f} | {m.recall_at_k:.2f} | {m.mrr:.3f} |")
    print()

    print("| Consulta | Documento esperado | Semântica | BM25 | Híbrida |")
    print("|---|---|---|---|---|")
    detalhes = zip(*(m.detalhes for m in metodos.values()), strict=True)
    for s, b, h in detalhes:
        posicoes = [str(d.posicao) if d.posicao else f"fora do top {k}" for d in (s, b, h)]
        print(f"| {s.consulta} | `{s.esperado}` | " + " | ".join(posicoes) + " |")


if __name__ == "__main__":
    main()
