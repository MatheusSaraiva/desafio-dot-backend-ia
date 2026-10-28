"""Avaliação da busca: recall@k e MRR em consultas com resposta conhecida.

Também implementa um baseline lexical (BM25) para mostrar onde a busca semântica
ganha: as consultas abaixo foram escritas de propósito com palavras diferentes das
usadas nos documentos (sinônimos, paráfrases), que é o caso real de um aluno perguntando.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Protocol

from rank_bm25 import BM25Okapi

from .ingest import Chunk
from .search import ResultadoBusca

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


class Buscador(Protocol):
    def buscar(self, consulta: str, k: int = 5) -> list[ResultadoBusca]: ...


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


# ----------------------------------------------------------------- baseline BM25

_STOPWORDS = frozenset(
    "a o e de da do das dos em um uma uns umas para por com sem que se na no nas nos ao aos "
    "as os ou mas como mais muito ja nao sim seu sua seus suas ele ela eles elas voce isso "
    "isto esse essa este esta pelo pela ate entre sobre quando onde qual quais ser ter foi "
    "sao era sera pode podem tambem".split()
)


def tokenizar(texto: str) -> list[str]:
    """Minúsculas, sem acentos, só palavras, sem stopwords. Tokenizador simples de propósito."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [t for t in re.findall(r"\w+", sem_acento) if t not in _STOPWORDS and len(t) > 1]


class BuscadorBM25:
    """Baseline lexical com a mesma interface do buscador semântico (agrupa por documento)."""

    nome = "bm25"

    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenizar(c.texto_para_embedding) for c in chunks])

    def buscar(self, consulta: str, k: int = 5) -> list[ResultadoBusca]:
        scores = self.bm25.get_scores(tokenizar(consulta))
        ordem = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)
        resultados: list[ResultadoBusca] = []
        vistos: set[str] = set()
        for i in ordem:
            chunk = self.chunks[i]
            if chunk.doc_id in vistos:
                continue
            vistos.add(chunk.doc_id)
            resultados.append(
                ResultadoBusca(
                    doc_id=chunk.doc_id,
                    titulo=chunk.titulo,
                    fonte=chunk.fonte,
                    score=round(float(scores[i]), 4),
                    trecho=chunk.texto,
                    indice_chunk=chunk.indice,
                )
            )
            if len(resultados) == k:
                break
        return resultados
