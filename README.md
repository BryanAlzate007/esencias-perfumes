# Perfume Platform

Plataforma web enfocada en el mundo de los perfumes, diseñada para que los usuarios puedan descubrir fragancias, registrar sus compras, guardar sus gustos y preferencias, compartir opiniones y participar en una comunidad mediante comentarios y reseñas.

La aplicación estará disponible en **español e inglés**, será **responsive** para dispositivos móviles, tablets y computadores, y contará con **tema claro y oscuro**.

## 🚀 Tecnologías

### Frontend

* **React**
* **React Router DOM**
* **Bootstrap**
* **Axios**
* JavaScript
* Diseño responsive
* Internacionalización (ES / EN)
* Tema claro / oscuro

### Backend

* **Python**
* **Django**
* **Django REST Framework (DRF)**
* PostgreSQL
* API REST
* Autenticación basada en tokens/JWT
* Django ORM

### Infraestructura

La infraestructura podrá definirse posteriormente dependiendo del crecimiento del proyecto.

Una posible arquitectura:

```text
                    ┌─────────────────────┐
                    │       Usuario       │
                    └──────────┬──────────┘
                               │
                     Web / Mobile / Tablet
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React + Bootstrap │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                         REST API / HTTPS
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Django + DRF        │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    └─────────────────────┘
```

---

# 🎯 Objetivo

Crear una plataforma especializada en perfumes donde los usuarios puedan construir su propio perfil olfativo y llevar un historial de sus experiencias con diferentes fragancias.

El objetivo inicial es combinar:

* Catálogo de perfumes.
* Perfil personal.
* Registro de compras.
* Preferencias y gustos.
* Reseñas.
* Comentarios.
* Calificaciones.
* Historial de perfumes probados.
* Comunidad de usuarios.

La arquitectura debe permitir incorporar posteriormente nuevas funcionalidades sin tener que modificar completamente el sistema.

---

# 👤 Usuarios

Los usuarios podrán crear una cuenta y administrar su información personal relacionada con perfumes.

## Registro

El usuario podrá registrarse utilizando:

* Nombre de usuario.
* Nombre.
* Correo electrónico.
* Contraseña.
* País.
* Idioma preferido.

Posteriormente se podrán agregar métodos adicionales de autenticación como:

* Google.
* Apple.
* Otros proveedores OAuth.

## Inicio de sesión

El sistema permitirá:

* Iniciar sesión.
* Cerrar sesión.
* Recuperar contraseña.
* Cambiar contraseña.
* Actualizar información del perfil.

---

# 🌸 Perfil de usuario

Cada usuario tendrá un perfil relacionado con sus preferencias de perfumería.

Ejemplo:

```text
Usuario
│
├── Información personal
│
├── Preferencias
│   ├── Familias olfativas
│   ├── Notas favoritas
│   ├── Notas que no le gustan
│   ├── Estaciones preferidas
│   ├── Momentos de uso
│   └── Intensidad preferida
│
├── Perfumes
│   ├── Comprados
│   ├── Probados
│   ├── Favoritos
│   ├── Deseados
│   └── No me gustan
│
└── Reseñas
```

---

# 🧴 Catálogo de perfumes

La plataforma tendrá un catálogo de perfumes.

Cada perfume podrá contener información como:

* Nombre.
* Marca.
* Género.
* Año de lanzamiento.
* País de origen.
* Concentración.
* Familia olfativa.
* Notas de salida.
* Notas de corazón.
* Notas de fondo.
* Descripción.
* Imagen.
* Perfumista.
* Temporada recomendada.
* Momento recomendado para utilizarlo.

Ejemplo:

```json
{
  "name": "Perfume Example",
  "brand": "Brand Example",
  "gender": "unisex",
  "concentration": "Eau de Parfum",
  "release_year": 2025,
  "olfactive_family": "Woody",
  "top_notes": [],
  "middle_notes": [],
  "base_notes": []
}
```

---

# 🛒 Registro de compras

Los usuarios podrán registrar los perfumes que han comprado.

La compra no necesariamente representa una transacción realizada dentro de la plataforma.

Inicialmente funcionará como un **historial personal de compras**.

El usuario podrá registrar:

* Perfume.
* Fecha de compra.
* Tienda.
* Precio.
* Moneda.
* Cantidad.
* Tamaño del frasco.
* Presentación.
* Comentario personal.

Ejemplo:

```text
Mis compras

┌──────────────────────────────┐
│ Dior Sauvage EDP             │
│ Comprado: 15/08/2026         │
│ Tamaño: 100 ml               │
│ Precio: $120 USD              │
│ Tienda: Example Store        │
└──────────────────────────────┘
```

---

# ❤️ Preferencias

Los usuarios podrán indicar qué características de los perfumes les gustan.

Por ejemplo:

### Familias olfativas

* Cítrica
* Amaderada
* Floral
* Oriental
* Gourmand
* Aromática
* Chipre
* Cuero
* Acuática

### Notas

El usuario podrá seleccionar notas que:

* Le gustan.
* No le gustan.
* Le gustaría probar.

Esto permitirá construir posteriormente un **perfil olfativo**.

---

# ⭐ Reseñas

Los usuarios podrán publicar reseñas de perfumes.

Una reseña podrá contener:

* Calificación.
* Título.
* Comentario.
* Fecha.
* Experiencia personal.
* Duración percibida.
* Proyección percibida.
* Ocasión de uso.

Ejemplo:

```text
★★★★★

Excelente perfume para la noche

Duración: 9/10
Proyección: 8/10

"Lo utilicé durante una cena y recibí varios cumplidos..."
```

Las reseñas estarán asociadas a un usuario y a un perfume.

---

# 💬 Comentarios

Los usuarios podrán comentar las reseñas de otros usuarios.

Ejemplo:

```text
Bryan:
★★★★★
Me sorprendió mucho la duración.

Carlos:
¿Lo recomendarías para clima caliente?

Bryan:
Sí, pero usaría pocas atomizaciones.
```

Inicialmente los comentarios podrán ser simples.

Posteriormente se podrá implementar:

* Respuestas a comentarios.
* Likes.
* Reportes.
* Moderación.
* Notificaciones.

---

# 🔍 Búsqueda y descubrimiento

La plataforma deberá permitir buscar perfumes mediante diferentes criterios.

Ejemplos:

```text
Buscar:
"Sauvage"

Marca:
Dior

Familia:
Amaderada

Género:
Unisex

Precio:
$50 - $150

Notas:
Vainilla
Ámbar
Sándalo
```

También se podrán crear filtros combinados.

---

# 🤖 Recomendaciones

La arquitectura deberá permitir incorporar posteriormente un sistema de recomendaciones.

Por ejemplo:

```text
Perfil del usuario
        │
        ├── Notas favoritas
        ├── Familias favoritas
        ├── Perfumes comprados
        ├── Perfumes favoritos
        └── Reseñas
                │
                ▼
       Sistema de recomendaciones
                │
                ▼
      Perfumes potencialmente
           interesantes
```

Esta funcionalidad puede comenzar con reglas simples y posteriormente evolucionar hacia sistemas de recomendación más avanzados.

---

# 🌎 Internacionalización

La plataforma estará disponible inicialmente en:

* 🇪🇸 Español
* 🇺🇸 Inglés

El idioma deberá poder cambiarse desde la interfaz.

Ejemplo:

```text
Español
English
```

Los textos de la interfaz no deberán estar escritos directamente dentro de los componentes cuando sean susceptibles de traducción.

Ejemplo conceptual:

```javascript
t("perfumes.title")
```

En lugar de:

```javascript
<h1>Mis perfumes</h1>
```

La arquitectura deberá permitir agregar nuevos idiomas posteriormente.

---

# 🌓 Tema claro y oscuro

La aplicación tendrá dos temas:

### Light

```text
☀️ Tema claro
```

### Dark

```text
🌙 Tema oscuro
```

El usuario podrá cambiar el tema manualmente.

También se podrá contemplar posteriormente la opción:

```text
Sistema
```

para utilizar automáticamente la preferencia del sistema operativo.

La preferencia podrá almacenarse localmente para mantenerla entre sesiones.

---

# 📱 Responsive Design

La plataforma deberá funcionar correctamente en:

* 📱 Smartphones
* 📱 Tablets
* 💻 Laptops
* 🖥️ Monitores de escritorio

El diseño se construirá utilizando Bootstrap y deberá priorizar una experiencia **mobile-first**.

---

# 🏗️ Arquitectura del proyecto

Se propone separar completamente frontend y backend.

```text
perfume-platform/
│
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── accounts/
│   │   ├── perfumes/
│   │   ├── reviews/
│   │   ├── purchases/
│   │   ├── preferences/
│   │   └── core/
│   │
│   └── requirements/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── i18n/
│   │   ├── routes/
│   │   └── assets/
│   │
│   └── package.json
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

# 🔙 Backend

El backend será desarrollado con Django y Django REST Framework.

Las responsabilidades principales serán:

* Autenticación.
* Usuarios.
* Perfiles.
* Perfumes.
* Marcas.
* Notas.
* Familias olfativas.
* Compras.
* Favoritos.
* Preferencias.
* Reseñas.
* Comentarios.
* Calificaciones.
* API REST.

## Aplicaciones Django

### `accounts`

Responsable de:

* Usuarios.
* Autenticación.
* Registro.
* Perfil.
* Recuperación de contraseña.

### `perfumes`

Responsable de:

* Perfumes.
* Marcas.
* Notas.
* Familias olfativas.
* Concentraciones.

### `purchases`

Responsable de:

* Historial de compras.
* Tiendas.
* Precios.
* Presentaciones.

### `reviews`

Responsable de:

* Reseñas.
* Calificaciones.
* Comentarios.
* Likes.
* Reportes.

### `preferences`

Responsable de:

* Notas favoritas.
* Familias favoritas.
* Preferencias del usuario.
* Perfil olfativo.

### `core`

Elementos compartidos de la aplicación.

---

# 🔐 Autenticación

La autenticación se implementa con **django-allauth** en modo headless, pensado para el SPA de React.

Flujo:

```text
React
  │
  │ POST /_allauth/browser/v1/auth/login
  ▼
django-allauth (headless)
  │
  ▼
Sesión + cookie CSRF
  │
  │ credentials: include
  ▼
API REST (DRF SessionAuthentication)
```

El frontend habla con allauth en `/_allauth/browser/v1/` (login, registro, logout y recuperación de contraseña). El resto de la API (`/api/v1/`) usa la misma sesión.

Vite hace proxy de `/_allauth` y `/api` hacia Django para que las cookies funcionen en local (`localhost:5173`).

Se cubre:

* Registro.
* Inicio de sesión.
* Cierre de sesión.
* Recuperación de contraseña.
* Perfil (`/api/v1/me/`).
* Roles de usuario final y administrador.

---

# 🔌 API

La comunicación entre frontend y backend será mediante API REST.

Ejemplo:

```text
/api/v1/
│
├── auth/
├── users/
├── perfumes/
├── brands/
├── notes/
├── preferences/
├── purchases/
├── favorites/
├── reviews/
└── comments/
```

Ejemplo de endpoint:

```http
GET /api/v1/perfumes/
```

Respuesta:

```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "name": "Perfume Example",
      "brand": "Brand Example",
      "rating": 4.8
    }
  ]
}
```

---

# 🗄️ Modelo de datos inicial

Una posible estructura:

```text
User
 │
 ├── Profile
 │
 ├── Purchase
 │       │
 │       └── Perfume
 │
 ├── Preference
 │       │
 │       ├── Note
 │       └── OlfactiveFamily
 │
 ├── Favorite
 │       │
 │       └── Perfume
 │
 └── Review
         │
         ├── Perfume
         │
         └── Comment
```

Relaciones principales:

```text
Brand
  │
  └── Perfume
        │
        ├── Notes
        ├── Olfactive Family
        ├── Reviews
        ├── Purchases
        └── Favorites
```

---

# 🎨 Frontend

El frontend estará desarrollado con React.

Se recomienda mantener una separación clara entre:

```text
UI
 │
 ├── Components
 ├── Pages
 └── Layouts

Business Logic
 │
 ├── Hooks
 ├── Context
 └── Services

API
 │
 └── Axios
```

Ejemplo:

```text
src/
├── components/
│   ├── Navbar/
│   ├── PerfumeCard/
│   ├── ReviewCard/
│   └── Rating/
│
├── pages/
│   ├── Home/
│   ├── Login/
│   ├── Register/
│   ├── Perfumes/
│   ├── PerfumeDetail/
│   ├── Profile/
│   ├── Purchases/
│   └── Reviews/
│
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── perfumes.js
│   └── reviews.js
│
├── context/
│   ├── AuthContext.jsx
│   └── ThemeContext.jsx
│
└── i18n/
    ├── es/
    └── en/
```

---

# 🧪 Testing

El proyecto deberá incorporar pruebas desde las primeras etapas.

## Backend

Se utilizará el sistema de testing de Django/DRF para probar:

* Modelos.
* Serializers.
* Views.
* Endpoints.
* Permisos.
* Autenticación.

## Frontend

Se podrán incorporar pruebas para:

* Componentes.
* Hooks.
* Formularios.
* Servicios.
* Flujos principales.

---

# 🔒 Seguridad

La aplicación deberá considerar:

* HTTPS.
* django-allauth (sesión + CSRF).
* CORS correctamente configurado.
* CSRF cuando corresponda.
* Validación de datos.
* Permisos por usuario.
* Protección de endpoints.
* Rate limiting para endpoints sensibles.
* Sanitización y validación de contenido.
* Protección contra spam en reseñas y comentarios.

Los datos privados de un usuario no deberán ser accesibles mediante modificaciones manuales de IDs en las peticiones.

Ejemplo:

```http
GET /api/v1/users/15/purchases/
```

deberá verificar que el usuario autenticado tenga autorización para acceder a esos datos.

---

# 📈 Escalabilidad

El proyecto deberá diseñarse pensando en crecimiento progresivo.

Inicialmente:

```text
React
   │
Django REST Framework
   │
PostgreSQL
```

Posteriormente se podrán incorporar:

```text
                    ┌── Redis
                    │
React → API → Django ── Celery
                    │
                    └── PostgreSQL
```

Esto permitirá implementar posteriormente:

* Procesamiento asíncrono.
* Notificaciones.
* Recomendaciones.
* Procesamiento de imágenes.
* Importación masiva de perfumes.
* Emails.
* Tareas programadas.

---

# 🛠️ Instalación

## Requisitos

* Python 3.12+
* Node.js 20+
* PostgreSQL
* Docker y Docker Compose
* Git

## Clonar repositorio

```bash
git clone <repository-url>

cd perfume-platform
```

---

# Backend

Entrar al backend:

```bash
cd backend
```

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar:

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear archivo `.env`:

```env
DEBUG=True

SECRET_KEY=your-secret-key

DATABASE_NAME=perfume_platform
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Ejecutar migraciones:

```bash
python manage.py migrate
```

Crear superusuario:

```bash
python manage.py createsuperuser
```

Iniciar servidor:

```bash
python manage.py runserver
```

API disponible en:

```text
http://localhost:8000/
```

---

# Frontend

Entrar al frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

Iniciar servidor:

```bash
npm run dev
```

Frontend disponible normalmente en:

```text
http://localhost:5173/
```

---

# Docker

Copiar variables de entorno:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Levantar todos los servicios:

```bash
docker compose up --build
```

Servicios disponibles:

```text
Frontend: http://localhost:5173/
API:      http://localhost:8002/api/v1/health/
Admin:    http://localhost:8002/admin/
Postgres: localhost:5432
```

El backend se publica en el puerto `8002` para no chocar con otros servicios locales en `8000`. Dentro del contenedor Django sigue escuchando en `8000`.

Datos de demostración:

```bash
docker compose exec backend python manage.py seed_demo
```

Cuentas:

```text
Admin:   admin / Admin1234!
Usuario: bryan / User1234!  (bryanalzate007@gmail.com)
```

La recuperación de contraseña se envía a `bryanalzate007@gmail.com`. Para que llegue a la bandeja y no solo a la consola del backend, añade una [contraseña de aplicación de Gmail](https://myaccount.google.com/apppasswords) en `EMAIL_HOST_PASSWORD`.

---

# 🔧 Variables de entorno

Las variables sensibles nunca deberán almacenarse directamente en Git.

Ejemplo:

```env
SECRET_KEY=
DATABASE_URL=
CORS_ALLOWED_ORIGINS=
FRONTEND_URL=
```

El repositorio deberá incluir un archivo:

```text
.env.example
```

pero nunca:

```text
.env
```

---

# 🗺️ Roadmap

## Fase 1 — Base del proyecto

* [x] Crear repositorio.
* [x] Configurar Django.
* [x] Configurar DRF.
* [x] Configurar PostgreSQL.
* [x] Configurar React.
* [x] Configurar Bootstrap.
* [x] Configurar variables de entorno.
* [x] Configurar estructura de aplicaciones.

## Fase 2 — Usuarios

* [x] Registro.
* [x] Login.
* [x] Logout.
* [x] Autenticación con django-allauth (sesión headless).
* [x] Recuperación de contraseña.
* [x] Perfil.
* [x] Idioma según el navegador del visitante.
* [x] Tema claro/oscuro según el sistema del visitante.

## Fase 3 — Catálogo

* [ ] Marcas.
* [ ] Perfumes.
* [ ] Familias olfativas.
* [ ] Notas.
* [ ] Concentraciones.
* [ ] Búsqueda.
* [ ] Filtros.
* [ ] Detalle del perfume.

## Fase 4 — Perfil olfativo

* [ ] Notas favoritas.
* [ ] Notas rechazadas.
* [ ] Familias favoritas.
* [ ] Perfumes favoritos.
* [ ] Lista de deseos.
* [ ] Perfumes probados.

## Fase 5 — Compras

* [ ] Registrar compra.
* [ ] Historial.
* [ ] Precio.
* [ ] Tienda.
* [ ] Presentación.
* [ ] Fecha de compra.

## Fase 6 — Comunidad

* [ ] Crear reseñas.
* [ ] Calificar perfumes.
* [ ] Comentarios.
* [ ] Likes.
* [ ] Reportar contenido.
* [ ] Moderación.

## Fase 7 — Recomendaciones

* [ ] Perfil olfativo.
* [ ] Recomendaciones basadas en preferencias.
* [ ] Recomendaciones basadas en perfumes similares.
* [ ] Sistema de puntuación.
* [ ] Historial de interacción.

## Fase 8 — Funcionalidades avanzadas

* [ ] Notificaciones.
* [ ] Recomendaciones inteligentes.
* [ ] Importación de perfumes.
* [ ] Estadísticas personales.
* [ ] Seguimiento de colección.
* [ ] Integración con tiendas.
* [ ] Aplicación móvil.

---

# 📊 Futuras estadísticas

Cada usuario podrá tener un dashboard personal.

Ejemplo:

```text
MI PERFIL

Perfumes en colección       32
Perfumes probados           47
Favoritos                   12
Reseñas escritas             8

Familia favorita:
Amaderada

Nota más frecuente:
Vainilla

Concentración preferida:
Eau de Parfum
```

Esto permitirá convertir los datos registrados por el usuario en información útil sobre sus propios gustos.

---

# 🌐 Visión futura

La plataforma no se limitará únicamente a ser un catálogo.

La visión es construir una **comunidad digital especializada en perfumes**, donde cada usuario pueda:

```text
Descubrir
   ↓
Conocer
   ↓
Probar
   ↓
Comprar
   ↓
Registrar
   ↓
Calificar
   ↓
Compartir
   ↓
Descubrir nuevos perfumes
```

A partir de la información proporcionada voluntariamente por los usuarios, la plataforma podrá generar perfiles olfativos y ofrecer experiencias personalizadas.

---

# 📄 Licencia

Definir licencia antes de publicar el proyecto.

---

# 👨‍💻 Desarrollo

Proyecto desarrollado con:

**Frontend:** React + Bootstrap

**Backend:** Django + Django REST Framework

**Database:** PostgreSQL

**Languages:** Español / Inglés

**Themes:** Light / Dark
