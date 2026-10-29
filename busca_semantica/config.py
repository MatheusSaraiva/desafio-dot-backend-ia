"""Configuração da busca semântica (variáveis de ambiente ou .env na raiz do repositório)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PACOTE_DIR = Path(__file__).resolve().parent
REPO_DIR = PACOTE_DIR.parent


class BuscaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Modelo de embeddings (HuggingFace). O e5-small é multilíngue, pequeno (~470 MB)
    # e bem avaliado em português; qualquer modelo do sentence-transformers funciona.
    embedding_model: str = "intfloat/multilingual-e5-small"
    corpus_dir: Path = PACOTE_DIR / "corpus"
    index_dir: Path = PACOTE_DIR / "index"
    # Tamanho em caracteres. O e5 lê no máximo 512 tokens e trunca em silêncio o que
    # passa; 1200 chars de português com código dão ~400 tokens, com folga. (Com 1500,
    # o maior chunk chegava a 496.) `build-index` imprime o maior chunk em tokens.
    chunk_size: int = 1200
    chunk_overlap: int = 150
    # Cosseno mínimo para um trecho contar como relevante (usado pelo RAG do chatbot).
    # Calibrado para o e5-small com `make evaluate`: a pior consulta com resposta dá 0,844
    # e a melhor consulta fora do domínio ("sintomas de gripe") dá 0,831; 0,837 é o ponto
    # médio. A margem é estreita, típica de modelo small. Trocou o modelo, recalibre.
    score_minimo: float = 0.837


settings = BuscaSettings()
