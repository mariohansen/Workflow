from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="WFS_")

    environment: Literal["local", "test", "production"] = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
