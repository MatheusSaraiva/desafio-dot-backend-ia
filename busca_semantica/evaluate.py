"""Avaliação da busca: recall@k e MRR em consultas com resposta conhecida, e calibração
do limiar de relevância (`score_minimo`).

As consultas abaixo foram escritas de propósito com palavras diferentes das usadas nos
documentos (sinônimos, paráfrases), que é o caso real de um aluno perguntando. É isso
que mostra onde a busca semântica ganha do baseline lexical (BM25, em `lexical.py`).
"""

from dataclasses import dataclass

from .search import Buscador, BuscadorSemantico

# (consulta, doc_id esperado). Paráfrases intencionais: pouca sobreposição lexical.
CONSULTAS_AVALIACAO: list[tuple[str, str]] = [
    ("como guardar vários valores em sequência e acrescentar novos no final", "listas"),
    ("coleção que não pode ser alterada depois de criada", "tuplas-e-imutabilidade"),
    ("estrutura para associar uma chave a um valor", "dicionarios"),
    ("eliminar repetidos de uma coleção", "conjuntos"),
    ("repetir um bloco de código para cada elemento", "loops-for-while"),
    ("como definir parâmetros opcionais com valor padrão", "funcoes"),
    ("gerar uma lista nova a partir de outra em uma única linha", "list-comprehension"),
    ("inserir o valor de uma variável dentro de um texto", "strings-e-fstrings"),
    ("ler o conteúdo de um csv linha por linha", "arquivos"),
    ("o que fazer quando o programa quebra com um erro", "excecoes"),
    ("reaproveitar atributos e métodos de outra classe", "classes-e-objetos"),
    ("instalar bibliotecas sem bagunçar o sistema", "modulos-pacotes-e-ambientes"),
    ("produzir valores um por vez sem carregar tudo na memória", "geradores-e-iteradores"),
    ("adicionar comportamento a uma função sem mexer no corpo dela", "decoradores"),
    ("indicar que um parâmetro deve ser inteiro", "type-hints"),
    ("verificar automaticamente se o código continua funcionando", "testes-com-pytest"),
    ("fazer o modelo de linguagem responder com base em documentos da empresa", "o-que-e-rag"),
    ("quando a IA deve passar a dúvida do aluno para uma pessoa", "tutoria-ia-e-mediacao-humana"),
    ("treinamento em pílulas curtas pelo celular", "microlearning-no-whatsapp"),
    ("como saber se o curso trouxe resultado para a empresa", "metricas-de-treinamento"),
    ("representar o significado de um texto como números", "embeddings-e-busca-semantica"),
    ("cuidados com dados pessoais dos alunos ao usar IA", "lgpd-e-ia-em-treinamentos"),
]

# Consultas que a base NÃO responde. O FAISS sempre devolve k vizinhos; é com estas que
# se escolhe o `score_minimo` que separa "parecido" de "irrelevante".
CONSULTAS_FORA_DO_DOMINIO: list[str] = [
    "receita de bolo de cenoura",
    "qual a capital da França",
    "como trocar o pneu do carro",
    "previsão do tempo para amanhã em Florianópolis",
    "melhor time de futebol do Brasil",
    "sintomas de gripe e o que tomar",
]


@dataclass(frozen=True)
class DetalheConsulta:
    consulta: str
    esperado: str
    posicao: int | None  # 1 = primeiro resultado; None = não apareceu no top-k
    primeiro: str | None


@dataclass(frozen=True)
class Metricas:
    recall_at_1: float
    recall_at_k: float
    mrr: float
    k: int
    detalhes: list[DetalheConsulta]


def avaliar(buscador: Buscador, consultas: list[tuple[str, str]], k: int = 3) -> Metricas:
    """recall@1, recall@k e MRR@k (média de 1/posição do documento esperado)."""
    acertos_1 = acertos_k = 0
    soma_rr = 0.0
    detalhes: list[DetalheConsulta] = []
    for consulta, esperado in consultas:
        ids = [r.doc_id for r in buscador.buscar(consulta, k=k)]
        posicao = ids.index(esperado) + 1 if esperado in ids else None
        if posicao == 1:
            acertos_1 += 1
        if posicao is not None:
            acertos_k += 1
            soma_rr += 1 / posicao
        detalhes.append(DetalheConsulta(consulta, esperado, posicao, ids[0] if ids else None))
    total = len(consultas) or 1
    return Metricas(
        recall_at_1=acertos_1 / total,
        recall_at_k=acertos_k / total,
        mrr=soma_rr / total,
        k=k,
        detalhes=detalhes,
    )


# ----------------------------------------------------------------- limiar de relevância


@dataclass(frozen=True)
class Calibracao:
    """Scores do 1º resultado: consultas com resposta na base vs. consultas fora do domínio."""

    no_dominio: list[tuple[str, float]]
    fora_do_dominio: list[tuple[str, float]]
    score_minimo: float | None  # o valor configurado, para conferir contra os dados

    @property
    def menor_no_dominio(self) -> float:
        return min(score for _, score in self.no_dominio)

    @property
    def maior_fora_do_dominio(self) -> float:
        return max(score for _, score in self.fora_do_dominio)

    @property
    def separa(self) -> bool:
        """O limiar configurado deixa passar tudo do domínio e barra tudo de fora?"""
        if self.score_minimo is None:
            return False
        return self.maior_fora_do_dominio < self.score_minimo <= self.menor_no_dominio

    @property
    def sugestao(self) -> float:
        """Ponto médio entre os dois grupos (só faz sentido se eles não se sobrepõem)."""
        return round((self.menor_no_dominio + self.maior_fora_do_dominio) / 2, 3)


def calibrar_score_minimo(
    semantico: BuscadorSemantico,
    consultas: list[tuple[str, str]] = CONSULTAS_AVALIACAO,
    fora_do_dominio: list[str] = CONSULTAS_FORA_DO_DOMINIO,
    score_minimo: float | None = None,
) -> Calibracao:
    """Mede o cosseno do 1º resultado em cada grupo. `semantico` deve estar SEM limiar."""
    if semantico.score_minimo is not None:
        raise ValueError("Calibre com um buscador sem score_minimo (senão os scores somem).")

    def top1(consulta: str) -> float:
        resultados = semantico.buscar(consulta, k=1)
        return resultados[0].score if resultados else 0.0

    return Calibracao(
        no_dominio=[(c, top1(c)) for c, _ in consultas],
        fora_do_dominio=[(c, top1(c)) for c in fora_do_dominio],
        score_minimo=score_minimo,
    )
