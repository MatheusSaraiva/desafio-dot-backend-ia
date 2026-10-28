"""Configuração do chatbot.

As chaves (OpenAI, LangSmith) ficam no `.env` da raiz, nunca no código. O `.env` é
carregado para o ambiente do processo porque o SDK da OpenAI e o LangSmith leem
`OPENAI_API_KEY` e `LANGSMITH_*` direto de `os.environ`.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_DIR = Path(__file__).resolve().parent.parent
load_dotenv(REPO_DIR / ".env")


class ChatSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: SecretStr | None = None
    # O enunciado cita GPT-4 (hoje legado). O modelo é configurável por env; o default é
    # um modelo atual e barato, suficiente para explicar Python com qualidade.
    openai_model: str = "gpt-5.4-mini"

    # Controles de custo e de robustez: limite de saída, timeout e retentativas do SDK.
    max_tokens: int = 1500
    timeout_segundos: float = 60.0
    max_retries: int = 2
    # Evita que uma entrada enorme (colar um arquivo inteiro) custe caro sem querer.
    tamanho_maximo_pergunta: int = 4000

    # Observabilidade (lidas também pelo SDK do LangSmith via ambiente).
    langsmith_tracing: bool = False
    langsmith_project: str = "dot-chatbot-python"


settings = ChatSettings()
