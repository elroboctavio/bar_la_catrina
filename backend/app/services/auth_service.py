# ============================================================
# services/auth_service.py — Lógica de negocio de Auth
# ============================================================
# Este archivo contiene las funciones "puras" de negocio:
#   - Crear y verificar tokens JWT
#   - Verificar contraseñas hasheadas
#   - Buscar usuarios en la BD
# Los routers llaman a estas funciones, no hacen la lógica ellos mismos.
# ============================================================

import bcrypt as _bcrypt

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.usuario import Usuario


# -------------------------------------------------------
# Funciones de contraseña (usando bcrypt directo)
# -------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash bcrypt almacenado."""
    return _bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt para almacenarla en la BD."""
    salt = _bcrypt.gensalt()
    return _bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# -------------------------------------------------------
# Funciones de JWT
# -------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT con los datos proporcionados y una fecha de expiración.

    Args:
        data: diccionario con los datos a codificar (ej: {"sub": username, "role": "Administrador"})
        expires_delta: tiempo de vida del token. Si es None, usa el valor del .env

    Returns:
        El JWT como string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.

    Returns:
        El payload del token si es válido, None si es inválido o expirado.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# -------------------------------------------------------
# Funciones de BD (async)
# -------------------------------------------------------

async def get_usuario_by_username(db: AsyncSession, username: str) -> Optional[Usuario]:
    """Busca un usuario en la BD por su nombre de usuario."""
    result = await db.execute(
        select(Usuario).where(Usuario.usuario == username)
    )
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario: busca en BD y verifica la contraseña.

    Returns:
        El objeto Usuario si las credenciales son válidas, None si no.
    """
    user = await get_usuario_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.contraseña):
        return None
    return user
