# ============================================================
# dependencies.py — Dependency Injection para FastAPI
# ============================================================
# FastAPI usa "dependencias" (Depends) para inyectar código
# reutilizable en los endpoints. Aquí definimos:
#
#   - get_current_user: valida el JWT y retorna el usuario
#   - require_admin: exige que el usuario sea Administrador
#
# Uso en un endpoint:
#   @router.get("/algo")
#   async def mi_endpoint(user = Depends(get_current_user)):
#       ...
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuario import Usuario
from app.services.auth_service import decode_access_token, get_usuario_by_username

# Esquema de seguridad: espera el header "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """
    Dependency que valida el JWT del header Authorization y retorna el usuario.
    Si el token es inválido o el usuario no existe, lanza 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales. Por favor inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificar que se envió el header Authorization
    if not credentials:
        raise credentials_exception

    # Decodificar el token
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # Extraer el username del payload (campo "sub" = subject)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Buscar el usuario en la BD (verificar que aún existe)
    user = await get_usuario_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user


async def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependency que además de autenticar, verifica que el usuario sea Administrador.
    Si no es admin, lanza 403 Forbidden.
    """
    if current_user.rol != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere rol de Administrador.",
        )
    return current_user
