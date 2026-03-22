"""
seed_admin.py — Crea el usuario administrador inicial en la BD.
Ejecutar una sola vez: python3 seed_admin.py

Uso:
    cd backend
    PYTHONPATH=. .venv/bin/python seed_admin.py
"""

import asyncio
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.services.auth_service import hash_password


async def seed():
    async with AsyncSessionLocal() as db:
        # Crear usuario administrador por defecto
        admin = Usuario(
            nombre="Administrador",
            ap_pat="Sistema",
            ap_mat=None,
            usuario="admin",
            contraseña=hash_password("admin1234"),
            rol="Administrador",
            telefono="0000000000",
            direccion="Bar La Catrina",
        )
        db.add(admin)
        await db.commit()
        print("✅ Usuario administrador creado:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin1234")
        print(f"   ⚠️  Cambia la contraseña después del primer login")


if __name__ == "__main__":
    asyncio.run(seed())
