# CLAUDE.md

Contexto permanente del proyecto **Administrador de Suscripciones** (ramo Arquitectura de Sistemas).
Este archivo es la fuente de verdad sobre *qué exige la evaluación* y *qué entra en el MVP*.

---

## 1. Requisitos de la entrega (PDF "Proyecto Monolito")

Son requisitos de **nota**, no opcionales. Antes de dar por cerrada una entrega, verificar uno por uno:

| # | Requisito | Estado actual |
|:--|:---|:---|
| 1 | Arquitectura **monolito**: un frontend + un backend, comunicados por REST, GraphQL o WebSockets (se pueden combinar) | ✅ Frontend React + backend FastAPI vía **REST** |
| 2 | **Backend dockerizado** | ❌ **Falta Dockerfile** — `docker-compose.yml` solo levanta Postgres y pgAdmin |
| 3 | **Coverage del backend ≥ 60%** | ⚠️ 85% medido en local (17-09-2026, 6 tests), pero el CI **no lo mide ni lo exige** |
| 4 | El proyecto debe funcionar **100%** según lo inscrito con el profesor (si no, nota máxima 3,9) | ⚠️ Frontend sigue siendo el boilerplate de Vite |
| 5 | Respetar el **stack tecnológico inscrito** | ✅ Ver sección 3 |
| 6 | **Pipeline en GitHub Actions** que como mínimo ejecute los tests (deseable: auto-deploy a un servicio gratuito) | ⚠️ CI corre lint + pytest; sin coverage ni deploy |
| 7 | **Material visual** para la presentación (temática, solución, diagramas) | ❌ Pendiente |

**Regla práctica:** cualquier cambio que rompa 2, 3 o 6 bloquea la entrega. Priorizar siempre esos sobre features nuevas.

---

## 2. MVP — alcance funcional (según el README)

La app permite **controlar gastos recurrentes en suscripciones**, unificando montos en distintas monedas.

### 2.1 Gestión de suscripciones y seguridad
- Registro y autenticación con **JSON Web Tokens** (OAuth2 password flow).
- Cada usuario tiene un entorno privado: solo ve y gestiona *sus* suscripciones.
- Una suscripción tiene: nombre del servicio, monto, moneda de origen y fecha de próximo cobro.

### 2.2 Motor de conversión y resumen financiero
- Cruza las suscripciones del usuario con la API externa de divisas (`exchangerate-api`).
- Calcula el **gasto total mensual en una moneda unificada** (ej. convertir cobros en USD a CLP en tiempo real).

### 2.3 Sistema de alertas
- El README lo declara ("sistema de alertas para notificar una próxima fecha de cobro") pero **no está implementado**.
- Es parte del MVP comprometido: si se mantiene en el README, hay que construirlo (endpoint de suscripciones próximas a vencer + aviso en el frontend).

### 2.4 Endpoints actuales

| Método | Endpoint | Descripción | Token |
|:---|:---|:---|:---:|
| `POST` | `/api/usuarios/` | Registro de usuario | No |
| `POST` | `/api/usuarios/login` | Login (form-data), retorna Bearer JWT | No |
| `GET` | `/api/usuarios/perfil` | Datos del usuario autenticado | Sí |
| `POST` | `/api/suscripciones/` | Registra una suscripción | Sí |
| `GET` | `/api/suscripciones/listar` | Lista las suscripciones del usuario | Sí |
| `GET` | `/api/suscripciones/resumen` | Total mensual consolidado con conversión (`?moneda=CLP`) | Sí |
| `GET` | `/api/conversion/` | Conversión puntual de un monto | No |
| `GET` | `/` | Health check | No |

---

## 3. Stack tecnológico inscrito

No cambiar sin avisar al profesor — el PDF exige respetarlo.

- **Backend:** FastAPI (Python), SQLModel + SQLAlchemy async, PostgreSQL (driver `asyncpg`).
- **Frontend:** React sobre Vite.
- **Auth:** OAuth2 + PyJWT, contraseñas hasheadas con SHA-256.
- **Integraciones:** `httpx` (async) contra `exchangerate-api`.
- **Testing/CI:** Pytest + pytest-cov, Ruff como linter, GitHub Actions con Postgres de servicio.

---

## 4. Estructura del repo

```
backend/
  main.py           # app FastAPI, lifespan que crea tablas, monta routers
  models.py         # Usuario, Suscripcion (SQLModel)
  config.py         # carga el .env y expone la configuración; único lugar que lee el entorno
  .env.example      # plantilla de variables (el .env real está en .gitignore)
  database.py       # engine async, init_db(), get_session()
  security.py       # crear_token_acceso(), decodificar_token()
  usuarios/         # router.py + services.py
  suscripciones/    # router.py + services.py
  conversion/       # router.py + services.py (API externa de divisas)
  tests/            # conftest.py + tests por módulo
frontend/           # React + Vite
.github/workflows/  # ci.yml
docker-compose.yml  # Postgres + pgAdmin
```

**Convención:** cada módulo de dominio es una carpeta con `router.py` (endpoints y DTOs) y `services.py` (lógica + acceso a datos). Mantenerla al agregar features nuevas — el router no debe consultar la base de datos directamente.

Código, comentarios, nombres de variables y mensajes de error **en español**.

---

## 5. Comandos

```bash
# Base de datos local
docker compose up -d

# Backend (desde backend/, con .venv activado)
pip install -r requirements-dev.txt
uvicorn main:app --reload          # http://127.0.0.1:8000  · docs en /docs

# Tests y coverage
pytest -v
pytest --cov=. --cov-report=term-missing   # debe quedar ≥ 60%

# Lint (mismo comando que corre el CI)
ruff check backend

# Frontend (desde frontend/)
npm install
npm run dev
```

Los tests levantan la app real contra la base de datos configurada en `database.py`, así que **Postgres debe estar corriendo** antes de `pytest`.

---

## 6. Deuda técnica conocida

Ordenada por impacto en la nota:

1. **Sin Dockerfile del backend** (requisito 2 del PDF). Falta también sumar el servicio `backend` al `docker-compose.yml`.
2. **CI no mide coverage** (requisito 3). El paso de tests debería ser `pytest backend --cov=backend --cov-fail-under=60`.
3. **Frontend sin implementar**: `src/App.jsx` es la plantilla de Vite. No hay login, listado, formulario ni cliente HTTP hacia la API.
4. **`POST /api/suscripciones/` recibe `usuario_id` en el body** en vez de derivarlo del token, como sí hacen `/listar` y `/resumen`. Permite crear suscripciones a nombre de otro usuario.
5. **Tests sin aislamiento**: `conftest.py` usa la base de datos real y los tests evitan colisiones con `int(time.time())` en los emails. Además, los tests de conversión golpean la API externa real, así que el CI depende de la red.
6. **Sistema de alertas ausente** (ver 2.3).
7. **Sin auto-deploy** en el pipeline (deseable según el PDF).
8. El README declara "React (TypeScript)" pero los archivos del frontend son `.jsx`.

---

## 7. Al trabajar en este proyecto

- Antes de cerrar una entrega, correr la checklist de la sección 1 completa.
- Si se agrega un endpoint, actualizar la tabla de la sección 2.4 **y** la del README.
- Si se agrega un módulo de dominio, agregar sus tests en `backend/tests/` — el coverage mínimo es parte de la nota.
- No introducir dependencias fuera del stack de la sección 3.
- **Nada de credenciales ni URLs en el código**: toda configuración pasa por `config.py`. Al agregar una variable, sumarla a `.env.example` y al bloque `env:` de [ci.yml](.github/workflows/ci.yml), o el pipeline se cae.
