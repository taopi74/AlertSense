"""Application settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    elastic_mcp_url: str = ""
    elastic_api_key: str = ""
    elastic_mcp_tool_name: str = "search_error_logs"

    elasticsearch_url: str = ""
    elasticsearch_api_key: str = ""

    demo_mode: bool = True
    port: int = 8080
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    @property
    def gemini_configured(self) -> bool:
        return bool(self.google_api_key)

    @property
    def elastic_mcp_configured(self) -> bool:
        return bool(self.elastic_mcp_url and self.elastic_api_key)

    @property
    def elasticsearch_configured(self) -> bool:
        return bool(self.elasticsearch_url and self.elasticsearch_api_key)

    @property
    def use_demo(self) -> bool:
        if self.demo_mode and not self.elastic_mcp_configured and not self.elasticsearch_configured:
            return True
        if not self.elastic_mcp_configured and not self.elasticsearch_configured:
            return True
        return False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
