# ============================================================
# routers/auth.py — Endpoints de autenticación
# ============================================================
# Tres endpoints:
#   POST /auth/login  → valida credenciales, devuelve JWT
#   POST /auth/logout → (stateless) instrucción al cliente de borrar el token
#   GET  /auth/me     → devuelve datos del usuario autenticado
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UserMe
from app.services.auth_service import authenticate_user, create_access_token

# El prefijo `/auth` se añade en main.py al registrar el router
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Inicia sesión con usuario y contraseña.

    - Valida las credenciales contra la BD
    - Si son correctas, retorna un JWT con los datos del usuario
    - Si son incorrectas, retorna 401

    El JWT debe guardarse en el cliente (cookie httpOnly recomendada)
    y enviarse en el header: `Authorization: Bearer <token>`
    """
    user = await authenticate_user(db, body.username, body.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token con el username como subject y el rol como claim adicional
    token = create_access_token(
        data={"sub": user.usuario, "role": user.rol, "id": user.id_usuario}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.rol,
        username=user.usuario,
        nombre_completo=f"{user.nombre} {user.ap_pat}",
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Cierra la sesión.

    Como JWT es stateless, el servidor no guarda el token.
    La "invalidación" real ocurre en el cliente (borrando la cookie/token).
    Este endpoint sirve para que el frontend tenga un punto unificado de logout.
    """
    return {"message": "Sesión cerrada correctamente."}


@router.get("/me", response_model=UserMe)
async def me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna los datos del usuario autenticado (excepto la contraseña).
    Requiere un JWT válido en el header Authorization.
    """
    return current_user
