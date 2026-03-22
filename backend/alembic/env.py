# ============================================================
# alembic/env.py — Configuración del entorno de migraciones
# ============================================================
# Este archivo configura cómo Alembic se conecta a la base de datos
# y descubre los modelos para generar migraciones automáticamente.
#
# Usamos el modo ASYNC porque nuestro engine es AsyncEngine.
# ============================================================

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Importar la Base de nuestros modelos para auto-detection
# (Alembic detecta los modelos registrados en Base.metadata)
from app.database import Base
from app.config import settings

# Importar TODOS los modelos para que Alembic los detecte
import app.models.usuario  # noqa: F401

# Configuración del logger de Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Le damos a Alembic los metadatos de nuestros modelos
target_metadata = Base.metadata

# Sobreescribir la URL de la BD con la del .env (ignora alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Modo offline: genera el SQL sin conectarse a la BD."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Modo online async: se conecta a la BD y aplica las migraciones."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Punto de entrada para el modo online (el más común)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
