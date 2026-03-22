# ============================================================
# config.py — Configuración centralizada con Pydantic Settings
# ============================================================
# Pydantic Settings lee automáticamente las variables del archivo .env
# y las hace disponibles como atributos tipados del objeto `settings`.
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Base de datos ---
    DATABASE_URL: str

    # --- JWT (JSON Web Tokens) ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas de sesión

    # --- App ---
    APP_NAME: str = "Bar La Catrina API"
    DEBUG: bool = False

    # Le dice a Pydantic que lea el archivo .env en la carpeta raíz del backend
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instancia global — importa `settings` desde cualquier módulo
settings = Settings()
