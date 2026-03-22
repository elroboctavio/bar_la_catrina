# ============================================================
# main.py — Punto de entrada de la aplicación FastAPI
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth


# -------------------------------------------------------
# Lifespan: código que se ejecuta al iniciar/detener la app
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Aquí puedes hacer setup inicial (ej: verificar conexión a BD)
    print(f"✅ {settings.APP_NAME} iniciando...")
    yield
    # Aquí puedes hacer cleanup al detener la app
    print(f"🛑 {settings.APP_NAME} detenido.")


# -------------------------------------------------------
# Instancia de FastAPI
# -------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="API REST del sistema de gestión Bar La Catrina",
    version="2.0.0",
    lifespan=lifespan,
    # Solo mostrar Swagger UI en modo debug
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# -------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------
# Permite que el frontend (Next.js en localhost:3000) haga
# requests al backend (FastAPI en localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Registro de Routers
# -------------------------------------------------------
app.include_router(auth.router)


# -------------------------------------------------------
# Endpoint raíz (health check)
# -------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": "2.0.0"}
