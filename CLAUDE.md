# CLAUDE.md

Contexto permanente del proyecto **Administrador de Suscripciones** (ramo Arquitectura de Sistemas).
Este archivo es la fuente de verdad sobre *qué exige la evaluación* y *qué entra en el MVP*.

---

## 1. Requisitos de la entrega (PDF "Proyecto Monolito")

Son requisitos de **nota**, no opcionales. Antes de dar por cerrada una entrega, verificar uno por uno:

| # | Requisito | Estado actual |
|:--|:---|:---|
| 1 | Arquitectura **monolito**: un frontend + un backend, comunicados por REST, GraphQL o WebSockets (se pueden combinar) | ✅ Frontend React + backend FastAPI vía **REST** |
| 2 | **Backend dockerizado** | ✅ `backend/Dockerfile` + servicio `backend` en `docker-compose.yml`; el CI construye la imagen |
| 3 | **Coverage del backend ≥ 60%** | ✅ 98% (23-09-2026, 31 tests), con `--cov-fail-under=60` exigido en el CI |
| 4 | El proyecto debe funcionar **100%** según lo inscrito con el profesor (si no, nota máxima 3,9) | ⚠️ Frontend sigue siendo el boilerplate de Vite |
| 5 | Respetar el **stack tecnológico inscrito** | ✅ Ver sección 3 |
| 6 | **Pipeline en GitHub Actions** que como mínimo ejecute los tests (deseable: auto-deploy a un servicio gratuito) | ⚠️ CI corre lint, tests con coverage y build de la imagen; falta el auto-deploy |
| 7 | **Material visual** para la presentación (temática, solución, diagramas) | ❌ Pendiente |

**Regla práctica:** cualquier cambio que rompa 2, 3 o 6 bloquea la entrega. Priorizar siempre esos sobre features nuevas.

---

## 2. MVP — alcance funcional (según el README)

La app permite **controlar gastos recurrentes en suscripciones**, unificando montos en distintas monedas.

### 2.1 Gestión de suscripciones y seguridad
- Registro y autenticación con **JSON Web Tokens** (OAuth2 password flow).
- Cada usuario tiene un entorno privado: solo ve y gestiona *sus* suscripciones — el `usuario_id` siempre se deriva del token vía `dependencies.obtener_usuario_actual`, nunca del body de la petición.
- Una suscripción tiene: nombre del servicio, monto, moneda de origen, fecha de próximo cobro, `activa` (bool, default `true`) y `periodicidad` (`"mensual"` o `"anual"`).
- Ciclo de vida completo: crear, editar (`PUT`, reemplazo completo de los 5 campos editables), desactivar y reactivar. El campo `activa` **solo** se cambia por sus endpoints dedicados, nunca por el `PUT`, para que haya una sola forma de hacer cada cosa.
- El navegador solo puede llamar a la API desde los orígenes de `CORS_ORIGINS` (ver §3). El token viaja en el header `Authorization`, no en cookies, por eso el middleware no habilita credenciales.

### 2.2 Motor de conversión y resumen financiero
- Cruza las suscripciones del usuario con la API externa de divisas (`exchangerate-api`).
- Calcula el **gasto total mensual en una moneda unificada** (ej. convertir cobros en USD a CLP en tiempo real).

### 2.3 Sistema de alertas
- Implementado en `backend/alertas/` como endpoint **on-demand**: el frontend consulta `GET /api/alertas/proximas` y muestra el aviso; no hay scheduler ni envío de correos.
- **Stateless**: la alerta no se persiste, se calcula en cada request desde `fecha_proximo_cobro`. No hay estado de "alerta vista/descartada" (si se quisiera, va en el frontend con `localStorage`).
- **Ventana simétrica**: con `?dias=7` devuelve desde `hoy - 7` hasta `hoy + 7`. Las vencidas recientes salen con `vencida: true` y `dias_restantes` negativo; las vencidas hace más de `dias` quedan fuera para no acumular ruido.
- Incluye el monto convertido a la moneda pedida (`?moneda=CLP`). Si la API de divisas falla, la alerta igual se entrega con `monto_convertido: null` en vez de fallar entera.
- Para avanzar la fecha tras un cobro existe `PATCH /api/suscripciones/{id}/renovar`, que suma **un ciclo** según `periodicidad` (nunca avanza solo: una lectura no escribe en la BD).

### 2.4 Endpoints actuales

| Método | Endpoint | Descripción | Token |
|:---|:---|:---|:---:|
| `POST` | `/api/usuarios/` | Registro de usuario | No |
| `POST` | `/api/usuarios/login` | Login (form-data), retorna Bearer JWT | No |
| `GET` | `/api/usuarios/perfil` | Datos del usuario autenticado (`id`, `nombre`, `email`, `rol`) | Sí |
| `POST` | `/api/suscripciones/` | Registra una suscripción (usuario derivado del token; recibe `periodicidad`) | Sí |
| `PUT` | `/api/suscripciones/{id}` | Edita una suscripción propia (mismo body que el registro; no toca `activa`) | Sí |
| `GET` | `/api/suscripciones/listar` | Lista las suscripciones del usuario (activas e inactivas) | Sí |
| `GET` | `/api/suscripciones/resumen` | Total mensual consolidado con conversión, **solo activas** (`?moneda=CLP`) | Sí |
| `PATCH` | `/api/suscripciones/{id}/desactivar` | Marca una suscripción propia como `activa=false` | Sí |
| `PATCH` | `/api/suscripciones/{id}/reactivar` | Vuelve a marcarla como `activa=true` | Sí |
| `PATCH` | `/api/suscripciones/{id}/renovar` | Avanza `fecha_proximo_cobro` un ciclo según `periodicidad` | Sí |
| `GET` | `/api/alertas/proximas` | Cobros dentro de la ventana `±dias` (`?dias=7&moneda=CLP`) | Sí |
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
  Dockerfile        # imagen del backend (python:3.14-slim, uvicorn en el puerto 8000)
  .dockerignore     # deja fuera .env, .venv y artefactos de tests
  main.py           # app FastAPI, lifespan que crea tablas, monta routers
  models.py         # Usuario, Suscripcion (SQLModel)
  config.py         # carga el .env y expone la configuración (incluye CORS_ORIGINS); único lugar que lee el entorno
  .env.example      # plantilla de variables (el .env real está en .gitignore)
  database.py       # engine async, init_db(), get_session()
  security.py       # crear_token_acceso(), decodificar_token(), oauth2_scheme
  dependencies.py   # obtener_usuario_actual(): dependencia compartida token -> Usuario
  usuarios/         # router.py + services.py
  suscripciones/    # router.py + services.py (incluye avanzar_fecha() para renovar)
  conversion/       # router.py + services.py (API externa de divisas)
  alertas/          # router.py + services.py (solo lectura: cobros próximos y vencidos)
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
# Stack completo dockerizado: Postgres + backend (:8000) + pgAdmin (:5050)
docker compose up -d --build

# Solo la base de datos, para desarrollar el backend en local
docker compose up -d db

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

Los tests levantan la app real contra la base de datos definida en `DATABASE_URL`, así que **Postgres debe estar corriendo** antes de `pytest`.

---

## 6. Deuda técnica conocida

Ordenada por impacto en la nota:

1. **Frontend sin implementar**: `src/App.jsx` es la plantilla de Vite. No hay login, listado, formulario ni cliente HTTP hacia la API. Es el mayor riesgo para la nota (requisito 4: tope de 3,9 si el proyecto no funciona).
2. ~~`POST /api/suscripciones/` recibe `usuario_id` en el body~~ — **corregido** (rama `fix-bugs`): el DTO ya no acepta `usuario_id`; se deriva siempre del token vía `dependencies.obtener_usuario_actual`, igual que `/listar` y `/resumen`.
3. **Tests sin aislamiento**: `conftest.py` usa la base de datos real y los tests evitan colisiones con `int(time.time())` en los emails. Además, los tests de conversión golpean la API externa real, así que el CI depende de la red.
4. ~~`/api/suscripciones/resumen` suma también las desactivadas~~ — **corregido** (rama `fixes-backend`): `obtener_suscripciones_por_usuario` acepta `solo_activas` y `calcular_gasto_total` la usa. `/listar` sigue devolviendo todas, a propósito, para que el frontend muestre el historial.
5. **Sin auto-deploy** en el pipeline (deseable según el PDF).
6. **`backend/.coverage` está versionado**: es un artefacto binario de `pytest-cov`, debería ir al `.gitignore` y salir del índice.
7. El README declara "React (TypeScript)" pero los archivos del frontend son `.jsx`.
8. El coverage reportado (98%) incluye los propios archivos de test, que siempre dan 100%; sin ellos el número real es más bajo. Se puede afinar con un `.coveragerc` que los excluya.
9. ~~`security.py` capturaba `except jwt.JWTError`~~ — **corregido** (rama `fix-bugs`): esa excepción no existe en PyJWT (es de `python-jose`), así que un token malformado no expirado producía un `AttributeError` no capturado → 500 en vez de 401. Ahora captura `jwt.PyJWTError`.
10. Contraseñas con SHA-256 sin salt (`usuarios/services.py`), comparación no constant-time. Conocido, fuera de alcance de `fix-bugs` — requiere migrar a una librería tipo `passlib`/`bcrypt`, cambio más grande.

---

## 7. Al trabajar en este proyecto

- Antes de cerrar una entrega, correr la checklist de la sección 1 completa.
- Si se agrega un endpoint, actualizar la tabla de la sección 2.4 **y** la del README.
- Si se agrega un módulo de dominio, agregar sus tests en `backend/tests/` — el coverage mínimo es parte de la nota.
- No introducir dependencias fuera del stack de la sección 3.
- **Nada de credenciales ni URLs en el código**: toda configuración pasa por `config.py`. Al agregar una variable, sumarla a `.env.example` y al bloque `env:` de [ci.yml](.github/workflows/ci.yml), o el pipeline se cae.
