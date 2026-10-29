"""Configuração do chatbot.

As chaves (OpenAI, DeepSeek, LangSmith) ficam no `.env` da raiz, nunca no código. O `.env`
é carregado para o ambiente do processo porque os SDKs dos provedores e o LangSmith leem
`OPENAI_API_KEY`, `DEEPSEEK_API_KEY` e `LANGSMITH_*` direto de `os.environ`.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_DIR = Path(__file__).resolve().parent.parent
load_dotenv(REPO_DIR / ".env")

# Provedores suportados -> variável com a chave e modelo sugerido. Para adicionar outro
# (Anthropic, Gemini...), basta instalar o pacote `langchain-<provedor>` e incluir aqui.
PROVEDORES = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}
MODELOS_SUGERIDOS = {
    "openai": "gpt-5.4-mini",
    "deepseek": "deepseek-flash",
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
    # Quantos chunks da base de conhecimento entram no prompt (~300 tokens cada).
    rag_trechos: int = 4

    # Observabilidade (lidas também pelo SDK do LangSmith via ambiente).
    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "dot-chatbot-python"

    @field_validator("openai_api_key", "deepseek_api_key", "langsmith_api_key", mode="before")
    @classmethod
    def _ignorar_placeholder(cls, valor):
        """Chave vazia ou o texto do .env.example conta como "não configurada"."""
        if valor is None:
            return None
        texto = valor.get_secret_value() if isinstance(valor, SecretStr) else str(valor)
        texto = texto.strip()
        return None if not texto or texto.startswith("coloque") else valor

    @property
    def provedor(self) -> str:
        return self.llm_model.partition(":")[0]

    @property
    def nome_do_modelo(self) -> str:
        return self.llm_model.partition(":")[2]

    @property
    def tracing_ativo(self) -> bool:
        """Tracing só conta como ligado com uma chave de verdade."""
        return self.langsmith_tracing and self.langsmith_api_key is not None

    def chave_do_provedor(self, provedor: str | None = None) -> SecretStr | None:
        chaves = {"openai": self.openai_api_key, "deepseek": self.deepseek_api_key}
        return chaves.get(provedor or self.provedor)

    def dica_de_alternativa(self) -> str:
        """Se outro provedor tem chave configurada, diz como usá-lo. Vazio se não houver."""
        alternativas = [
            f"LLM_MODEL={p}:{MODELOS_SUGERIDOS[p]}"
            for p in PROVEDORES
            if p != self.provedor and self.chave_do_provedor(p) is not None
        ]
        if not alternativas:
            return ""
        return " Há chave de outro provedor no .env; para usá-lo, defina " + " ou ".join(
            alternativas
        )


settings = ChatSettings()

if not settings.tracing_ativo:
    # O SDK do LangSmith decide pelo ambiente. Com LANGSMITH_TRACING=true e a chave vazia
    # ou com o placeholder do .env.example, ele tentaria enviar cada chamada e imprimiria
    # "403 Forbidden" no terminal a cada pergunta. Desligar aqui evita isso.
    os.environ["LANGSMITH_TRACING"] = "false"
