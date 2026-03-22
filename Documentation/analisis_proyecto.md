# 🍹 Análisis del Proyecto: Bar La Catrina

## ¿Qué es este proyecto?

**Bar La Catrina** es un **sistema de gestión de punto de venta (POS)** para un bar, desarrollado con Python/Flask y PostgreSQL. Es una aplicación web monolítica orientada al personal interno del bar (meseros y administradores).

---

## 🗂️ Arquitectura actual

```
Flask (Python)  →  PostgreSQL
     │
     └── Jinja2 Templates (HTML renderizado en servidor)
              │
              └── Flask-Bootstrap (CSS/UI)
```

| Archivo | Rol |
|---|---|
| [app.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/app.py) | Núcleo de la app — 1,044 líneas con todas las rutas |
| [db.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/db.py) | Pool de conexiones a PostgreSQL via `psycopg2` |
| [forms.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/forms.py) | Formulario de login con Flask-WTF |
| [utils.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/utils.py) | Validación de extensiones de imagen |
| [requirements.txt](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/requirements.txt) | Dependencias del entorno |

---

## ⚙️ Funcionalidades del sistema

### 🔐 Autenticación y Roles
- Login/Logout con sesiones de Flask
- Contraseñas hasheadas con `werkzeug`
- Dos roles: **Administrador** y **usuario estándar** (mesero)
- Decoradores `@login_required` y `@admin_required` protegen rutas

### 👥 Gestión de Usuarios *(solo Admin)*
- CRUD completo: registrar, ver, editar, eliminar usuarios
- Campos: nombre completo, usuario, contraseña, rol, fecha nacimiento, teléfono, dirección, foto
- Cálculo automático de edad desde `f_nacimiento`
- Subida de imagen de perfil (PNG, JPG, GIF)

### 📦 Gestión de Productos *(solo Admin)*
- CRUD completo de productos con: nombre, precio, categoría, contenido, stock, marca, código de barras
- Subida de imagen del producto
- Vista de catálogo con **paginación** y búsqueda por nombre o categoría

### 🏷️ Gestión de Categorías
- CRUD completo de categorías de bebidas/alimentos

### 🪑 Gestión de Mesas
- CRUD completo: número de mesa y ubicación (interior/exterior/etc.)

### 💰 Gestión de Ventas *(módulo central)*
- **Registrar venta**: selección de mesa, cliente, forma de pago, múltiples productos con cantidades
- Cálculo automático de subtotales y total
- Asocia la venta al usuario (mesero) en sesión
- Vista de ventas con **filtro por rango de fechas**
- Los meseros solo ven sus propias ventas; el admin ve todas
- **Detalles de venta**: lista itemizada de productos en cada venta

### 🖨️ Reportes PDF
- **Ticket de venta individual** (PDF generado con `pdfkit` + `wkhtmltopdf`)
- **Reporte de ventas** por rango de fechas en PDF
- Compatible con Windows y Linux

---

## 🗃️ Estructura de la Base de Datos (inferida del código)

```
usuario          → id_usuario, img, nombre, ap_pat, ap_mat, usuario, contraseña, rol, f_nacimiento, telefono, direccion
categoria        → id_cat, nombre_cat
productos        → id_prod, img, nombre, precio_u, fk_cat, contenido, stock, marca, cod_barras
mesa             → id_mesa, num_mesa, ubicacion
ventas           → id_venta, fecha_venta, cant_prod, total, forma_pago, fk_mesa, fk_usuario, nombre_cliente
detalles_venta   → id_det, fk_venta, fk_producto, subtotal, cantidad, categoria_prod, nombre_prod, contenido_prod, precio_prod, cod_barras_prod
perfil_producto  → (Vista SQL que une productos + categorías)
```

---

## ⚠️ Problemas técnicos identificados

| Problema | Descripción |
|---|---|
| **Monolito gigante** | [app.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/app.py) tiene 1,044 líneas — todo en un solo archivo |
| **SQL Injection** | En [ver_ventas](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/app.py#789-831) y [reporte_ventas](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/app.py#927-970), las fechas se insertan con f-strings directamente en el query sin parámetros |
| **Credenciales expuestas** | Usuario y contraseña de PostgreSQL en texto plano en [db.py](file:///home/brian/Documentos/Proyects/bar_la_catrina/app/db.py) |
| **`app.run()` en módulo** | `app.run(debug=1)` está en el nivel del módulo, no bajo `if __name__ == '__main__'` |
| **Falta de ORM** | SQL raw en todos lados — dificulta mantenimiento y migración |
| **Sin pruebas** | No hay archivos de test |
| **Sin variables de entorno** | No usa `.env` para configuración sensible |
| **Flask-Bootstrap obsoleto** | La versión 3.3.7.1 usa Bootstrap 3, muy desactualizado |
| **wkhtmltopdf** | Herramienta deprecada y con builds inconsistentes entre sistemas |

---

---

# 🚀 Viabilidad de Reconstrucción con Tecnologías Modernas

## Veredicto general: **MUY VIABLE** ✅

El proyecto tiene una lógica de negocio clara y bien delimitada. La reconstrucción no es compleja — el sistema no tiene integraciones externas complejas, machine learning, ni microservicios. Es un CRUD bien definido con autenticación y generación de PDFs.

---

## Stack moderno recomendado

### Opción A — Full-Stack Web App (Recomendado para equipo web)

| Capa | Tecnología | Por qué |
|---|---|---|
| **Backend API** | **FastAPI** (Python) | Async, tipado, documentación automática (Swagger), mantiene Python |
| **ORM** | **SQLAlchemy 2.x + Alembic** | Migraciones, queries tipadas, evita SQL raw |
| **BD** | **PostgreSQL** | Misma base, sin cambios |
| **Frontend** | **Next.js 14** (React) | SSR + SPA, excelente UI, TypeScript |
| **UI Components** | **shadcn/ui + Tailwind** | Componentes modernos y accesibles |
| **Auth** | **JWT + httpOnly cookies** | Seguro, stateless |
| **PDF** | **Puppeteer o WeasyPrint** | Reemplazo moderno de wkhtmltopdf |
| **Archivos** | **S3 / Cloudflare R2** o local con validación | Para imágenes de productos/usuarios |
| **Config** | **Pydantic Settings + `.env`** | Variables de entorno seguras |

### Opción B — Solo refactorizar Flask (Menor esfuerzo)

Si no se quiere cambiar de stack, se puede modernizar el mismo proyecto:
- Separar en **Blueprints** (usuarios, productos, ventas, etc.)
- Usar **Flask-SQLAlchemy** en lugar de psycopg2 raw
- Agregar **python-dotenv** para variables de entorno
- Reemplazar Flask-Bootstrap 3 por **Bootstrap 5** directo
- Usar **WeasyPrint** en lugar de pdfkit/wkhtmltopdf
- Agregar **pytest** para pruebas

---

## Estimación de esfuerzo

| Módulo | Complejidad | Horas estimadas |
|---|---|---|
| Auth (login/logout/roles) | Baja | 4-6 h |
| CRUD Usuarios | Baja | 6-8 h |
| CRUD Productos + Categorías | Baja | 6-8 h |
| CRUD Mesas | Muy baja | 2-3 h |
| Registro de Ventas (multi-producto) | Media | 10-14 h |
| Historial y filtrado de Ventas | Baja-Media | 6-8 h |
| Generación de PDF (tickets/reportes) | Media | 6-10 h |
| Paginación y búsqueda | Baja | 3-4 h |
| Setup de proyecto, BD, deploy | Baja | 4-6 h |
| **Total estimado** | | **~47-67 horas** |

> Para un desarrollador con experiencia en el stack, en 2-3 semanas de trabajo a tiempo parcial.

---

## Mejoras que una reconstrucción permitiría

- 📱 **Responsive real** — interfaz usable desde tablet/celular del mesero
- 🔒 **Seguridad mejorada** — JWT, CSRF automático, variables de entorno
- ⚡ **API REST** — posibilidad de conectar app móvil o tablet en el futuro
- 📊 **Dashboard de ventas** — gráficas en tiempo real (Chart.js / Recharts)
- 🔔 **Notificaciones** — WebSockets para alertas entre meseros y cocina
- 🧾 **Impresión directa** — integración con impresoras térmicas via navegador
- 🧪 **Tests automatizados** — garantía de calidad en cada cambio
- 🛡️ **Sin SQL Injection** — ORM elimina el riesgo actual
