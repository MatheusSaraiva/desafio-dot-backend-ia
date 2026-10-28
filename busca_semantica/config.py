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
    # Tamanho em caracteres. ~1500 chars ≈ 300-400 tokens: cabe com folga no limite do
    # modelo (512 tokens) e mantém um assunto por chunk.
    chunk_size: int = 1500
    chunk_overlap: int = 150


settings = BuscaSettings()
