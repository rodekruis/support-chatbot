"""Application settings loaded from environment variables."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed application configuration used by the service layer."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    port: int = Field(default=8000, alias="PORT")

    # Deployment environment (e.g. "prod", "dev"). Used to namespace the vector
    # store indexes so a non-prod deployment never overwrites the prod data.
    # "prod" keeps the bare index name for backward compatibility.
    environment: str = Field(default="prod", alias="ENVIRONMENT")

    auth_api_key: SecretStr = Field(alias="AUTH_API_KEY")
    auth_api_key_write: SecretStr = Field(alias="AUTH_API_KEY_WRITE")

    vector_store_address: str = Field(alias="VECTOR_STORE_ADDRESS")
    vector_store_password: SecretStr = Field(alias="VECTOR_STORE_PASSWORD")

    azure_openai_endpoint: str = Field(alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: SecretStr = Field(alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(alias="AZURE_OPENAI_API_VERSION")

    model_chat: str = Field(alias="MODEL_CHAT")
    model_embeddings: str = Field(alias="MODEL_EMBEDDINGS")
    # Optional, evaluation-only: a separate (ideally stronger) deployment used as
    # the LLM-as-judge in the offline RAG quality tests. Kept distinct from
    # MODEL_CHAT so a model never grades its own output (self-preference bias).
    model_judge: str | None = Field(default=None, alias="MODEL_JUDGE")

    # Optional, observability-only: self-hosted Langfuse for LLM tracing. When
    # both keys are unset, tracing is disabled and the app behaves as before.
    langfuse_host: str | None = Field(default=None, alias="LANGFUSE_BASE_URL")
    langfuse_public_key: SecretStr | None = Field(
        default=None, alias="LANGFUSE_PUBLIC_KEY"
    )
    langfuse_secret_key: SecretStr | None = Field(
        default=None, alias="LANGFUSE_SECRET_KEY"
    )
