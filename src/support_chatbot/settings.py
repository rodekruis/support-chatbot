"""Application settings loaded from environment variables."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed application configuration used by the service layer."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    port: int = Field(default=8000, alias="PORT")

    auth_api_key: SecretStr = Field(alias="AUTH_API_KEY")
    auth_api_key_write: SecretStr = Field(alias="AUTH_API_KEY_WRITE")

    vector_store_address: str = Field(alias="VECTOR_STORE_ADDRESS")
    vector_store_password: SecretStr = Field(alias="VECTOR_STORE_PASSWORD")
    vector_store_id: str = Field(alias="VECTOR_STORE_ID")

    azure_openai_endpoint: str = Field(alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: SecretStr = Field(alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(alias="AZURE_OPENAI_API_VERSION")

    model_chat: str = Field(alias="MODEL_CHAT")
    model_embeddings: str = Field(alias="MODEL_EMBEDDINGS")
