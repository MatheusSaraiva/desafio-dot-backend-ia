"""Configuração do chatbot.

As chaves (OpenAI, DeepSeek, LangSmith) ficam no `.env` da raiz, nunca no código. O `.env`
é carregado para o ambiente do processo porque os SDKs dos provedores e o LangSmith leem
`OPENAI_API_KEY`, `DEEPSEEK_API_KEY` e `LANGSMITH_*` direto de `os.environ`.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_DIR = Path(__file__).resolve().parent.parent
load_dotenv(REPO_DIR / ".env")

# Provedores suportados -> nome da variável com a chave. Para adicionar outro (Anthropic,
# Gemini...), basta instalar o pacote `langchain-<provedor>` e incluir a linha aqui.
PROVEDORES = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


class ChatSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Modelo no formato `provedor:modelo`, como o `init_chat_model` do LangChain espera.
    # O enunciado cita GPT-4 (hoje legado); o padrão é um modelo atual e barato da OpenAI.
    # Alternativa: `deepseek:deepseek-flash` (API compatível com a da OpenAI, custo menor).
    llm_model: str = "openai:gpt-5.4-mini"
    openai_api_key: SecretStr | None = None
    deepseek_api_key: SecretStr | None = None

    # Controles de custo e de robustez: limite de saída, timeout e retentativas do SDK.
    max_tokens: int = 1500
    timeout_segundos: float = 60.0
    max_retries: int = 2
    # Evita que uma entrada enorme (colar um arquivo inteiro) custe caro sem querer.
    tamanho_maximo_pergunta: int = 4000

    # Observabilidade (lidas também pelo SDK do LangSmith via ambiente).
    langsmith_tracing: bool = False
    langsmith_project: str = "dot-chatbot-python"

    @property
    def provedor(self) -> str:
        return self.llm_model.partition(":")[0]

    @property
    def nome_do_modelo(self) -> str:
        return self.llm_model.partition(":")[2]

    def chave_do_provedor(self) -> SecretStr | None:
        return {"openai": self.openai_api_key, "deepseek": self.deepseek_api_key}.get(self.provedor)


settings = ChatSettings()
