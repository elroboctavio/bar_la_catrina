# ============================================================
# models/usuario.py — Modelo ORM de la tabla usuario
# ============================================================
# Este modelo mapea la tabla `usuario` en PostgreSQL.
# SQLAlchemy genera el SQL de CREATE TABLE a partir de este
# modelo, y Alembic lo usa para crear las migraciones.
# ============================================================

from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    # Mapped[tipo] le dice a SQLAlchemy (y a tu editor) el tipo del campo
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    img: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    ap_pat: Mapped[str] = mapped_column(String(100), nullable=False)
    ap_mat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # nombre de usuario para login (único)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # contraseña hasheada con bcrypt
    contraseña: Mapped[str] = mapped_column(String(255), nullable=False)

    # "Administrador" | "Mesero"
    rol: Mapped[str] = mapped_column(String(50), nullable=False, default="Mesero")

    f_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Usuario id={self.id_usuario} usuario={self.usuario} rol={self.rol}>"
