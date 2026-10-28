"""Carregamento do corpus e divisão em chunks.

Cada documento é um arquivo Markdown com um cabeçalho (front matter) simples:

    ---
    title: Listas em Python
    slug: listas
    tags: python, estruturas de dados
    ---
    corpo do artigo...

O `slug` vira o identificador do documento; sem slug, usa-se o nome do arquivo.
"""

from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class Documento:
    doc_id: str
    titulo: str
    fonte: str
    tags: tuple[str, ...]
    texto: str


@dataclass(frozen=True)
class Chunk:
    """Pedaço de um documento, com metadados suficientes para citar a origem."""

    doc_id: str
    titulo: str
    fonte: str
    indice: int
    texto: str

    @property
    def texto_para_embedding(self) -> str:
        # O título entra no texto vetorizado: um chunk do meio do artigo continua
        # "sabendo" de que assunto ele trata, o que melhora bastante a recuperação.
        return f"{self.titulo}\n\n{self.texto}"


def _separar_front_matter(conteudo: str) -> tuple[dict[str, str], str]:
    """Separa o cabeçalho `--- ... ---` do corpo. Parser propositalmente simples."""
    if not conteudo.startswith("---"):
        return {}, conteudo.strip()
    _, bloco, corpo = conteudo.split("---", 2)
    meta: dict[str, str] = {}
    for linha in bloco.strip().splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            meta[chave.strip().lower()] = valor.strip()
    return meta, corpo.strip()


def carregar_corpus(pasta: Path) -> list[Documento]:
    """Lê todos os `.md` da pasta, em ordem alfabética (determinístico)."""
    documentos: list[Documento] = []
    for caminho in sorted(pasta.glob("*.md")):
        meta, corpo = _separar_front_matter(caminho.read_text(encoding="utf-8"))
        if not corpo:
            continue
        tags = tuple(t.strip() for t in meta.get("tags", "").split(",") if t.strip())
        documentos.append(
            Documento(
                doc_id=meta.get("slug") or caminho.stem,
                titulo=meta.get("title") or caminho.stem,
                fonte=meta.get("source") or caminho.name,
                tags=tags,
                texto=corpo,
            )
        )
    if not documentos:
        raise FileNotFoundError(f"Nenhum documento .md encontrado em {pasta}")
    return documentos


def dividir_em_chunks(
    documentos: list[Documento], chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    """Divide cada documento em pedaços de até `chunk_size` caracteres.

    O splitter recursivo tenta cortar primeiro em parágrafos, depois linhas, depois
    frases, para não partir uma ideia no meio. O overlap repete o fim do chunk anterior
    no início do próximo, assim uma frase na fronteira não se perde.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[Chunk] = []
    for doc in documentos:
        for indice, pedaco in enumerate(splitter.split_text(doc.texto)):
            chunks.append(
                Chunk(
                    doc_id=doc.doc_id,
                    titulo=doc.titulo,
                    fonte=doc.fonte,
                    indice=indice,
                    texto=pedaco.strip(),
                )
            )
    return chunks
