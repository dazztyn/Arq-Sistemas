# Administrador de Suscripciones

Mini app-web monolítica que permite gestionar suscripciones a distintos servicios para controlar y hacer seguimiento de gastos frecuentes, integrando conversiones de moneda con actualización de valor en tiempo real y un sistema de alertas para notificar una próxima fecha de cobro.

## Características Principales:

1. **Gestión de Suscripciones y Seguridad:** 
   Sistema de registro y autenticación basado en **JSON Web Tokens**. Cada usuario tiene un entorno privado y seguro para agregar, listar y gestionar sus suscripciones o gastos mensuales asignando montos, monedas de origen y fechas de cobro. 

2. **Motor de Conversión y Resumen Financiero:** 
   El sistema unifica los gastos del usuario cruzando la información de sus suscripciones con una API externa de divisas (`exchangerate-api`). La cuál permite calcular el gasto total  en una moneda unificada (por ejemplo, convirtiendo los cobros en USD a CLP de forma automática y en tiempo real). Como el total es **mensual**, las suscripciones anuales aportan solo su doceava parte.

3. **Sistema de Alertas de Cobro:**
   Informa qué suscripciones se cobran dentro de una ventana configurable de días (por defecto 7, hacia adelante y hacia atrás), indicando cuántos días faltan, el monto convertido a la moneda elegida y si el cobro ya venció. Las alertas se calculan al momento de la consulta a partir de la fecha de próximo cobro, y tras un cobro la suscripción se pone al día con el endpoint de renovación, que avanza la fecha un ciclo según su periodicidad (mensual o anual).

4. **Interfaz web:**
   Aplicación React que consume la API por REST. Incluye registro e inicio de sesión, un dashboard con el gasto mensual y la distribución por servicio, el ciclo completo de gestión de suscripciones y el panel de próximos cobros. La sesión se cierra sola y redirige al login cuando el token expira.

## Stack Tecnológico

* **Frameworks:** FastAPI (Python), React sobre Vite (JavaScript / JSX)
* **ORM & Base de Datos:** SQLModel + SQLAlchemy async, PostgreSQL (driver `asyncpg`)
* **Autenticación:** OAuth2 con PyJWT (Hashed passwords con SHA-256)
* **Testing & CI:** Pytest + pytest-cov y Ruff como linter, sobre GitHub Actions con PostgreSQL levantado como servicio del runner. El pipeline exige un mínimo de 60% de cobertura (`--cov-fail-under=60`) y construye la imagen Docker del backend.
* **Integraciones:** Consumo de APIs REST asíncronas con `httpx`.

## Ejecución con Docker (recomendado)

El backend está dockerizado y el `docker-compose.yml` levanta el stack completo: PostgreSQL, la API y pgAdmin.

```bash
git clone <URL_DEL_REPOSITORIO>
cd Arq-Sistemas
cp backend/.env.example backend/.env   # completa SECRET_KEY
docker compose up -d --build
```

| Servicio | URL |
|:---|:---|
| API | http://localhost:8000 (documentación en `/docs`) |
| PostgreSQL | `localhost:5432` |
| pgAdmin | http://localhost:5050 |

`docker compose up -d db` levanta solo la base de datos, si prefieres correr el backend desde tu entorno local.

## Instalación y Ejecución Local

### 1. **Clonar el repositorio y entrar a la carpeta:**
 ```bash
 git clone <URL_DEL_REPOSITORIO>
 cd Arq-Sistemas/backend
```

### 2. **Crear y activar entorno virtual:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. **Instalar dependencias:**
```bash
pip install -r requirements.txt

# Para correr los tests y el linter, usa el archivo de desarrollo:
pip install -r requirements-dev.txt
```

### 4. **Variables de Entorno:**
El backend lee toda su configuración del entorno (`backend/config.py`). Copia la plantilla y completa tus valores locales:
```bash
cp .env.example .env
```
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/suscripciones_db
SECRET_KEY=<genera la tuya>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
```
`CORS_ORIGINS` define desde qué orígenes puede llamar el navegador a la API (varios se separan por coma). El valor por defecto es el puerto de desarrollo de Vite.
`SECRET_KEY` es obligatoria y no tiene valor por defecto: si falta, la aplicación no arranca. Genera una con:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. **Iniciar la aplicación:**
```bash
uvicorn main:app --reload
```
La API quedará disponible en http://127.0.0.1:8000.

> **Importante:** el backend puede levantarse de dos formas, y ambas ocupan el puerto 8000. Para desarrollar, usa `docker compose up -d db` (solo la base de datos) y luego uvicorn. Si levantas el stack completo con `docker compose up -d`, el contenedor `backend` toma el puerto y sirve la última imagen construida, no tu código actual: en ese caso reconstruye con `docker compose up -d --build`.

## Frontend

El frontend es una app React que consume la API. Necesita el backend corriendo.

### 1. **Instalar dependencias:**
```bash
cd frontend
npm install
```

### 2. **Variables de entorno:**
```bash
cp .env.example .env
```
```bash
VITE_API_URL=http://127.0.0.1:8000
```
Es la URL del backend. Si apunta a otro lado, el navegador recibirá errores de CORS salvo que esa dirección esté en `CORS_ORIGINS` del backend.

### 3. **Iniciar:**
```bash
npm run dev
```
La app queda en http://localhost:5173.

### Qué incluye

Registro e inicio de sesión con JWT, dashboard con el gasto mensual consolidado y la distribución por servicio, formulario para crear y editar suscripciones, activación y desactivación, y un panel de próximos cobros con un botón para registrar que ya te cobraron, que avanza la fecha un ciclo.

El gasto mensual y los próximos cobros se piden al backend (`/resumen` y `/alertas/proximas`) en lugar de calcularse en el navegador, para que la cifra que ve el usuario sea siempre la misma que entrega la API.

## Endpoints

### Usuario:
| Método | Endpoint | Descripción | Requiere Token |
|:---|:---|:---|:---:|
| `POST` | `/api/usuarios/` | Registro de un nuevo usuario | No |
| `POST` | `/api/usuarios/login` | Login (form-data) que retorna el Bearer JWT | No |
| `GET` | `/api/usuarios/perfil` | Retorna los datos del usuario autenticado (`id`, `nombre`, `email`, `rol`) | Sí |

### Suscripciones:
| Método | Endpoint | Descripción | Requiere Token |
|:---|:---|:---|:---:|
| `POST` | `/api/suscripciones/` | Registra una nueva suscripción para el usuario autenticado (`nombre_servicio`, `monto_original`, `moneda_original`, `fecha_proximo_cobro`, `periodicidad`) | Sí |
| `PUT` | `/api/suscripciones/{id}` | Edita una suscripción propia (mismo body que el registro) | Sí |
| `GET` | `/api/suscripciones/listar` | Lista todas las suscripciones registradas del usuario | Sí |
| `GET` | `/api/suscripciones/resumen` | Retorna el total mensual consolidado con conversión (solo suscripciones activas; las anuales se prorratean a 1/12) | Sí |
| `PATCH` | `/api/suscripciones/{id}/desactivar` | Marca una suscripción propia como inactiva | Sí |
| `PATCH` | `/api/suscripciones/{id}/reactivar` | Vuelve a marcar una suscripción propia como activa | Sí |
| `PATCH` | `/api/suscripciones/{id}/renovar` | Avanza la fecha de cobro un ciclo según su periodicidad | Sí |

### Alertas:
| Método | Endpoint | Descripción | Requiere Token |
|:---|:---|:---|:---:|
| `GET` | `/api/alertas/proximas` | Cobros dentro de la ventana `±dias` (`?dias=7&moneda=CLP`), con monto convertido y marca de vencido | Sí |

### Conversión y estado:
| Método | Endpoint | Descripción | Requiere Token |
|:---|:---|:---|:---:|
| `GET` | `/api/conversion/` | Conversión puntual de un monto (`?monto=100&origen=USD&destino=CLP`) | No |
| `GET` | `/` | Health check de la API | No |
