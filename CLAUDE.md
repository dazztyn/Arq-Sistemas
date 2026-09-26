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
| 3 | **Coverage del backend ≥ 60%** | ✅ 34 tests. El CI reporta 86% (incluye los archivos de test); medido solo sobre el código fuente es 96%. Ver deuda #8 |
| 4 | El proyecto debe funcionar **100%** según lo inscrito con el profesor (si no, nota máxima 3,9) | ✅ Frontend implementado e integrado con la API: login, dashboard, CRUD, alertas y renovación |
| 5 | Respetar el **stack tecnológico inscrito** | ✅ Ver sección 3 |
| 6 | **Pipeline en GitHub Actions** que como mínimo ejecute los tests (deseable: auto-deploy a un servicio gratuito) | ⚠️ CI corre lint, tests con coverage y build de la imagen. El CD a Railway está escrito en `.github/workflows/cd-railway.yml.ejemplo` pero todavía inactivo |
| 7 | **Material visual** para la presentación (temática, solución, diagramas) | ⚠️ En curso: presentación en Canva (portada, problemática, stack, arquitectura, módulos, demo). Faltan las capturas del pipeline y del stack dockerizado |

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
- El total es **mensual**, así que una suscripción `anual` aporta `monto / 12` (`monto_mensual()` en `suscripciones/services.py`). Se prorratea *antes* de convertir: la conversión es lineal, así que el orden da igual, pero así la periodicidad se aplica en un solo lugar.
- Si la API de divisas responde con un error HTTP, `convertir_moneda` lo traduce a 400 (moneda de origen desconocida, la API devuelve 404) o 503 (falla del servicio). Nunca deja escapar la excepción de `httpx`.

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
| `GET` | `/api/suscripciones/resumen` | Total mensual consolidado con conversión, **solo activas**, anuales prorrateadas a 1/12 (`?moneda=CLP`) | Sí |
| `PATCH` | `/api/suscripciones/{id}/desactivar` | Marca una suscripción propia como `activa=false` | Sí |
| `PATCH` | `/api/suscripciones/{id}/reactivar` | Vuelve a marcarla como `activa=true` | Sí |
| `PATCH` | `/api/suscripciones/{id}/renovar` | Avanza `fecha_proximo_cobro` un ciclo según `periodicidad` | Sí |
| `GET` | `/api/alertas/proximas` | Cobros dentro de la ventana `±dias` (`?dias=7&moneda=CLP`) | Sí |
| `GET` | `/api/conversion/` | Conversión puntual de un monto | No |
| `GET` | `/` | Health check | No |

### 2.5 Cómo el frontend consume la API

- **El token.** `login()` (en `utils/AuthContext.jsx`) pide el token a `/login`, luego el perfil, y guarda ambos en `localStorage` **y en el estado de React**. El estado es la fuente de verdad mientras la app corre: así, al cerrar sesión, todos los componentes se enteran en el mismo render. El token se toma siempre de `useAuth()`, nunca leyendo `localStorage` desde un componente.
- **El 401 no es un error más.** `solicitar()` lo convierte en `SesionExpirada`; el hook cierra la sesión y redirige a `/login` con el motivo. Sin eso, al expirar el token (60 min) la app queda rota hasta que alguien recargue.
- **El dashboard no recalcula lo que ya calcula la API.** El total sale de `/resumen` y los próximos cobros de `/alertas/proximas`. Si se replicaran en el cliente, mostrarían números distintos a los de la API — pasó con el prorrateo de las anuales.
- **Las tres lecturas van con `Promise.allSettled`, no con `all`.** El resumen y las alertas dependen de la API externa de divisas; con `all`, una caída de ese servicio dejaba al usuario sin ver **ninguna** suscripción, aunque el listado no la necesite. Si el total no se puede calcular se muestra un guion, no un cero: un cero se leería como "no gastas nada".
- **La conversión se pide una vez por moneda distinta**, no una por suscripción, y se multiplica en el cliente. La tasa se pide con un monto base alto porque el backend redondea a 2 decimales.
- **Fechas.** Se usa el string `YYYY-MM-DD` del backend tal cual, sin pasar por `toISOString()`, que según la zona horaria devuelve el día anterior.

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
frontend/
  .env.example      # VITE_API_URL: URL del backend
  src/
    main.jsx        # monta BrowserRouter + AuthProvider
    App.jsx         # rutas; /dashboard va envuelta en ProtectedRoute
    pages/          # Landing, Login, Register, Dashboard, NotFound
    components/     # Navbar + dashboard/ (CifraCard, GraphCard, ListaSuscripcion,
                    #   FormularioSuscripcion, ProximosCobros)
    hooks/          # useSubscriptions.jsx: carga los datos y expone las acciones
    services/       # Auth.service.ts y Subscripciones.service.ts: única capa que hace fetch
    utils/          # AuthProvider.js (contexto), AuthContext.jsx (provider), useAuth, ProtectedRoute
.github/workflows/  # ci.yml + cd-railway.yml.ejemplo (borrador del CD, inactivo)
docker-compose.yml  # Postgres + backend + pgAdmin
```

**Convención (backend):** cada módulo de dominio es una carpeta con `router.py` (endpoints y DTOs) y `services.py` (lógica + acceso a datos). Mantenerla al agregar features nuevas — el router no debe consultar la base de datos directamente.

**Convención (frontend):** ningún componente llama a `fetch` directamente. Todo pasa por `services/`, y los componentes reciben los datos del hook `useSubscriptions`. Es el equivalente de la separación router/services del backend.

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

1. ~~**Frontend sin implementar**~~ — **resuelto** (rama `integracion-front`): la app tiene login, registro, dashboard, CRUD completo, alertas y renovación, conectada a la API. Verificado de punta a punta en navegador: el total del dashboard coincide con el de `/resumen`.
2. ~~`POST /api/suscripciones/` recibe `usuario_id` en el body~~ — **corregido** (rama `fix-bugs`): el DTO ya no acepta `usuario_id`; se deriva siempre del token vía `dependencies.obtener_usuario_actual`, igual que `/listar` y `/resumen`.
3. **Tests sin aislamiento**: `conftest.py` usa la base de datos real y los tests evitan colisiones con `int(time.time())` en los emails. Además, los tests de conversión golpean la API externa real, así que el CI depende de la red.
4. ~~`/api/suscripciones/resumen` suma también las desactivadas~~ — **corregido** (rama `fixes-backend`): `obtener_suscripciones_por_usuario` acepta `solo_activas` y `calcular_gasto_total` la usa. `/listar` sigue devolviendo todas, a propósito, para que el frontend muestre el historial.
5. **Sin auto-deploy** en el pipeline (deseable según el PDF). Al montarlo, ojo con dos cosas: `SECRET_KEY` y `DATABASE_URL` deben venir de GitHub Secrets (los del `env:` de `ci.yml` son desechables, solo para los tests), y **`CORS_ORIGINS` debe apuntar a la URL pública del frontend**. Como esa variable tiene valor por defecto en `config.py`, si se olvida el backend arranca igual y el fallo solo se ve en la consola del navegador; ahí habrá que decidir si conviene quitarle el default para que falle ruidosamente.
6. **`backend/.coverage` está versionado**: es un artefacto binario de `pytest-cov`, debería ir al `.gitignore` y salir del índice.
7. ~~El README declara "React (TypeScript)" pero los archivos del frontend son `.jsx`~~ — **corregido**: el README ya dice "React sobre Vite (JavaScript / JSX)". Quedan 2 archivos `.ts` en `services/`, el resto es `.jsx`.
8. **El coverage está mal medido, en las dos direcciones.** El 86% que reporta el CI incluye los propios archivos de test, que siempre dan 100%. Pero medirlo solo sobre el código fuente da 76%, que **también es falso**: SQLAlchemy async ejecuta el trabajo de BD dentro de greenlets y `coverage` no traza ahí sin configurarlo. El número real es **96%**. Se arregla con un `.coveragerc` que tenga `omit = */tests/*` **y** `concurrency = thread,greenlet`.
9. ~~`security.py` capturaba `except jwt.JWTError`~~ — **corregido** (rama `fix-bugs`): esa excepción no existe en PyJWT (es de `python-jose`), así que un token malformado no expirado producía un `AttributeError` no capturado → 500 en vez de 401. Ahora captura `jwt.PyJWTError`.
10. Contraseñas con SHA-256 sin salt (`usuarios/services.py`), comparación no constant-time. Conocido, fuera de alcance de `fix-bugs` — requiere migrar a una librería tipo `passlib`/`bcrypt`, cambio más grande.
11. ~~`/resumen` sumaba las suscripciones anuales completas al total **mensual**~~ — **corregido** (rama `fixes-backend-2te2vt`): una anual de 120.000 se contaba como 120.000/mes. Ahora se prorratea con `monto_mensual()`. Cubierto por `test_resumen_prorratea_las_anuales`.
12. ~~`convertir_moneda` no capturaba `httpx.HTTPStatusError`~~ — **corregido** (rama `fixes-backend-2te2vt`): `raise_for_status()` lanza esa excepción, que **no** es subclase de `RequestError` (ambas cuelgan de `httpx.HTTPError`), así que un error HTTP de la API se escapaba y el backend devolvía 500. De paso rompía la resiliencia de las alertas, porque `alertas/_convertir_monto` solo atrapa `HTTPException`.
13. **Una llamada HTTP por suscripción** en `calcular_gasto_total` y en las alertas: si el usuario tiene 10 suscripciones en USD se piden 10 veces la misma tasa, en serie y sin caché. Con pocos datos no se nota, pero es la optimización obvia (agrupar por moneda o pedir las tasas de la moneda destino una sola vez).
14. **Registro con condición de carrera**: `crear_usuario` consulta y después inserta, sin capturar `IntegrityError`. Dos registros simultáneos con el mismo email dan 500 en vez de 400. La restricción `unique` de la BD igual protege el dato.
15. **El token se guarda en `localStorage`**, así que queda expuesto a XSS. Aceptable para el alcance del ramo; la alternativa sería una cookie `httpOnly`, que obliga a habilitar credenciales en CORS y cambia el flujo de auth completo.
16. **Nombres invertidos en `frontend/src/utils/`**: `AuthProvider.js` define el *contexto* y `AuthContext.jsx` define el *provider*. Confunde al leerlo; renombrarlos es un cambio mecánico que se evitó para no ensuciar el diff de la integración.
17. **El frontend no tiene tests.** El coverage que exige la pauta es solo del backend, así que no afecta la nota, pero la lógica de `useSubscriptions` (prorrateo mostrado, ventana de alertas, manejo del 401) no tiene red de seguridad.

---

## 7. Al trabajar en este proyecto

- Antes de cerrar una entrega, correr la checklist de la sección 1 completa.
- Si se agrega un endpoint, actualizar la tabla de la sección 2.4 **y** la del README.
- Si se agrega un módulo de dominio, agregar sus tests en `backend/tests/` — el coverage mínimo es parte de la nota.
- No introducir dependencias fuera del stack de la sección 3.
- **Nada de credenciales ni URLs en el código**: toda configuración pasa por `config.py`. Al agregar una variable, sumarla a `.env.example` y al bloque `env:` de [ci.yml](.github/workflows/ci.yml), o el pipeline se cae.
- **Autoría de los commits**: `.claude/settings.json` deja `attribution` en vacío, así que los commits no llevan líneas de `Co-Authored-By` ni de sesión. Eso no cubre el campo `author` de git, que sale de la config del entorno: en una sesión en la nube el contenedor arranca con la identidad de Claude, así que **antes del primer commit** hay que fijarla con `git config user.name "Vicente Ruiz Escobar"` y `git config user.email "greatdazz3@gmail.com"` (no se versiona, se pierde con el contenedor).
