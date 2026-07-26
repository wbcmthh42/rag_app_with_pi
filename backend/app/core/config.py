from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
DEFAULT_PDF_PATH = REPO_ROOT / "data" / "barbie.pdf"
DEFAULT_VECTORSTORE_DIR = BACKEND_ROOT / "data" / "vectorstore"
DEFAULT_ENV_PATH = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(DEFAULT_ENV_PATH), env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    model_api_key: str = Field(default="replace-me", alias="MODEL_API_KEY")
    model_base_url: str = Field(default="https://api.openai.com/v1", alias="MODEL_BASE_URL")
    chat_model: str = Field(default="gpt-4o-mini", alias="CHAT_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    azure_api_version: str = Field(default="2024-02-01", alias="AZURE_API_VERSION")
    azure_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_chat_deployment: str = Field(default="", alias="AZURE_CHAT_DEPLOYMENT")
    azure_embedding_deployment: str = Field(default="", alias="AZURE_EMBEDDING_DEPLOYMENT")
    pdf_source_path: Path = Field(default=DEFAULT_PDF_PATH, alias="PDF_SOURCE_PATH")
    vectorstore_dir: Path = Field(default=DEFAULT_VECTORSTORE_DIR, alias="VECTORSTORE_DIR")
    session_ttl_minutes: int = Field(default=30, alias="SESSION_TTL_MINUTES")
    rate_limit_requests_per_minute: int = Field(default=20, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_burst: int = Field(default=5, alias="RATE_LIMIT_BURST")
    top_k_results: int = Field(default=4, alias="TOP_K_RESULTS")

    @property
    def metadata_path(self) -> Path:
        return self.vectorstore_dir / "metadata.json"

    @property
    def chunks_path(self) -> Path:
        return self.vectorstore_dir / "chunks.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.vectorstore_dir.mkdir(parents=True, exist_ok=True)
    return settings
