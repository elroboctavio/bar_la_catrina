# Bar La Catrina POS

Sistema de Punto de Venta (POS) para Bar La Catrina. Este proyecto está compuesto por un backend en Python con FastAPI y un frontend moderno creado con Next.js.

## 🚀 Tecnologías

### Backend

- **FastAPI**: Framework web de alto rendimiento.
- **SQLAlchemy (Async)**: ORM asíncrono.
- **PostgreSQL / asyncpg**: Base de datos relacional.
- **Alembic**: Migraciones de base de datos.
- **JWT & bcrypt**: Autenticación y seguridad.
- **Uvicorn**: Servidor ASGI.

### Frontend

- **Next.js 16**: Framework de React.
- **React 19**: Biblioteca para construir interfaces de usuario.
- **Tailwind CSS v4 / Shadcn**: Estilos y componentes visuales.
- **TypeScript**: Tipado estático para mayor mantenibilidad.

## 📋 Requisitos Previos

- **Node.js**: v20 o superior
- **Python**: v3.10 o superior
- **PostgreSQL**: Servidor de base de datos instalado y en ejecución

## 🛠️ Instalación y Configuración

### 1. Backend

1. Navegar al directorio del backend:

   ```bash
   cd backend
   ```

2. Crear un entorno virtual:

   ```bash
   python -m venv .venv
   ```

3. Activar el entorno virtual:

   - **Linux/macOS:** `source .venv/bin/activate`
   - **Windows:** `.venv\Scripts\activate`

4. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Configurar las variables de entorno:
   Copiar el archivo `.env.example` a `.env` y ajustar los valores requeridos, por ejemplo la cadena de conexión de la base de datos y la llave secreta para JWT.

   ```bash
   cp .env.example .env
   ```

6. Inicializar y correr las migraciones en la base de datos:

   ```bash
   alembic upgrade head
   ```

7. Ejecutar el servidor en desarrollo:

   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Frontend

1. Navegar al directorio del frontend:

   ```bash
   cd frontend
   ```

2. Instalar las dependencias:

   ```bash
   npm install
   ```

3. Configurar las variables de entorno:
   Crear un archivo `.env.local` y definir la URL de la API del backend si es necesario (el frontend se comunica de manera predeterminada a `http://localhost:8000` si así está configurado).

4. Ejecutar el servidor de desarrollo:

   ```bash
   npm run dev
   ```

## 📚 Estructura del Proyecto

- `backend/`: Código de la API RESTful (FastAPI), modelos de SQLAlchemy, esquemas (Pydantic), y lógica de validación/autenticación.
- `frontend/`: Código fuente de la interfaz web responsiva (Next.js, App Router, React Components).
- `Documentation/`: Archivos con el diseño, arquitectura y notas (ej. "Login y logout").
