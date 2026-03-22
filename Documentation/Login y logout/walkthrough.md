# ✅ Módulo 1 Completado: Auth/Login

## Lo que se construyó

El módulo de autenticación completo para el sistema Bar La Catrina v2, con el stack moderno (FastAPI + Next.js 16).

---

## Backend (FastAPI + async SQLAlchemy)

| Archivo | Descripción |
|---|---|
| [backend/app/config.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/config.py) | Pydantic Settings — lee [.env](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/.env) automáticamente |
| [backend/app/database.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/database.py) | Motor async SQLAlchemy con `asyncpg` |
| [backend/app/models/usuario.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/models/usuario.py) | Modelo ORM tabla [usuario](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/app.py#184-200) |
| [backend/app/schemas/auth.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/schemas/auth.py) | Pydantic schemas: [LoginRequest](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/schemas/auth.py#19-23), [TokenResponse](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/schemas/auth.py#29-36), [UserMe](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/schemas/auth.py#38-53) |
| [backend/app/services/auth_service.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/services/auth_service.py) | JWT create/decode + bcrypt hash/verify |
| [backend/app/dependencies.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/dependencies.py) | [get_current_user](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/dependencies.py#28-62) + [require_admin](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/dependencies.py#64-75) dependencies |
| [backend/app/routers/auth.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/routers/auth.py) | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| [backend/app/main.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/backend/app/main.py) | FastAPI app + CORS + router registration |
| `backend/alembic/` | Migración inicial aplicada a `bar_la_catrina_v2` |
| `backend/seed_admin.py` | Usuario admin creado: `admin / admin1234` |

**Base de datos creada:** `bar_la_catrina_v2`

## Frontend (Next.js 16 + Tailwind + shadcn/ui)

| Archivo | Descripción |
|---|---|
| `frontend/src/proxy.ts` | Protección de rutas (Next.js 16 proxy convention) |
| `frontend/src/lib/api.ts` | Funciones fetch hacia FastAPI |
| `frontend/src/app/api/auth/route.ts` | API Route: maneja JWT como cookie httpOnly |
| `frontend/src/app/login/page.tsx` | Página de login (Server Component + diseño premium) |
| `frontend/src/components/LoginForm.tsx` | Formulario de login (Client Component) |
| `frontend/src/app/dashboard/page.tsx` | Dashboard con módulos role-based |
| `frontend/src/components/Navbar.tsx` | Navbar con usuario, rol y logout |

---

## Verificación (todos 6/6 ✅)

| Test | Resultado |
|---|---|
| `GET /` → redirige a `/login` | ✅ |
| Login con credenciales **incorrectas** → muestra error | ✅ |
| Login con credenciales **correctas** → redirige a `/dashboard` | ✅ |
| Dashboard muestra nombre, rol ámbar "Administrador" | ✅ |
| Click "Salir" → redirige a `/login` | ✅ |
| Acceso directo a `/dashboard` sin sesión → redirige a `/login` | ✅ |

---

## Capturas de pantalla

![Página de login con error de credenciales](/home/brian/.gemini/antigravity/brain/25f694e3-22ae-4d28-ae59-3de2a8f17125/login_error_wrong_creds_1774145614366.png)

![Dashboard con rol Administrador](/home/brian/.gemini/antigravity/brain/25f694e3-22ae-4d28-ae59-3de2a8f17125/dashboard_view_1774145638727.png)

![Vuelta al login tras logout](/home/brian/.gemini/antigravity/brain/25f694e3-22ae-4d28-ae59-3de2a8f17125/login_after_logout_1774145662684.png)

---

## Cómo iniciar los servidores

```bash
# Terminal 1 — Backend
cd backend
PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

| URL | Qué es |
|---|---|
| http://localhost:3000 | Aplicación Next.js |
| http://localhost:8000/docs | Swagger UI de FastAPI |

---

## Credenciales iniciales

| Campo | Valor |
|---|---|
| **Usuario** | `admin` |
| **Contraseña** | `admin1234` |

> ⚠️ Cambiar la contraseña del admin después del primer uso real.

---

## Gotchas aprendidos

- **Python 3.14 + passlib**: `passlib` tiene un bug con la nueva versión del módulo `bcrypt`. Se reemplazó con `bcrypt` directo.
- **Next.js 16**: El archivo `middleware.ts` fue renombrado a `proxy.ts` con export `proxy` (no `middleware`).
- **Uvicorn**: Usar `--host 0.0.0.0` para que sea accesible desde la LAN y para que el middleware/proxy de Next.js funcione correctamente.
