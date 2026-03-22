# ============================================================
# database.py — Motor async de SQLAlchemy + sesión de BD
# ============================================================
# SQLAlchemy 2.x con asyncpg permite hacer queries sin bloquear
# el event loop de FastAPI. Cada endpoint recibe una sesión
# AsyncSession inyectada via `get_db` (dependency injection).
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Motor async: se conecta a PostgreSQL usando asyncpg como driver
# echo=True imprime las queries SQL en consola (útil en desarrollo)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Fábrica de sesiones async — cada request obtiene una sesión nueva
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita lazy-loading tras commit
    autoflush=False,
    autocommit=False,
)


# Clase base para todos los modelos ORM
class Base(DeclarativeBase):
    pass


# -------------------------------------------------------
# Dependency injection para FastAPI
# -------------------------------------------------------
# Se usa con: db: AsyncSession = Depends(get_db)
# El `async with` garantiza que la sesión se cierre al terminar
# el request, aunque ocurra una excepción.
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
