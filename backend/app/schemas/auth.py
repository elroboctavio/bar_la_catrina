# ============================================================
# schemas/auth.py — Pydantic schemas para Auth
# ============================================================
# Los schemas de Pydantic definen la forma de los datos que
# entran y salen de la API. Son independientes de los modelos
# ORM (un schema puede exponer solo algunos campos del modelo).
# ============================================================

from datetime import date
from typing import Optional

from pydantic import BaseModel


# -------------------------------------------------------
# Request schemas (datos que el cliente ENVÍA a la API)
# -------------------------------------------------------

class LoginRequest(BaseModel):
    """Body del POST /auth/login"""
    username: str
    password: str


# -------------------------------------------------------
# Response schemas (datos que la API DEVUELVE al cliente)
# -------------------------------------------------------

class TokenResponse(BaseModel):
    """Respuesta exitosa del login con el JWT y datos básicos del usuario"""
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    nombre_completo: str


class UserMe(BaseModel):
    """Datos del usuario autenticado — expuesto por GET /auth/me"""
    id_usuario: int
    usuario: str
    nombre: str
    ap_pat: str
    ap_mat: Optional[str]
    rol: str
    f_nacimiento: Optional[date]
    telefono: Optional[str]
    direccion: Optional[str]
    img: Optional[str]

    # Permite que Pydantic lea datos directamente desde un objeto ORM
    model_config = {"from_attributes": True}
