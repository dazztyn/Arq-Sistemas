# Administrador de Suscripciones

Mini app-web monolítica que permite gestionar suscripciones a distintos servicios para controlar y hacer seguimiento de gastos frecuentes, integrando conversiones de moneda con actualización de valor en tiempo real y un sistema de alertas para notificar una próxima fecha de cobro.

## Características Principales:

1. **Gestión de Suscripciones y Seguridad:** 
   Sistema de registro y autenticación basado en **JSON Web Tokens**. Cada usuario tiene un entorno privado y seguro para agregar, listar y gestionar sus suscripciones o gastos mensuales asignando montos, monedas de origen y fechas de cobro. 

2. **Motor de Conversión y Resumen Financiero:** 
   El sistema unifica los gastos del usuario cruzando la información de sus suscripciones con una API externa de divisas (`exchangerate-api`). La cuál permite calcular el gasto total  en una moneda unificada (por ejemplo, convirtiendo los cobros en USD a CLP de forma automática y en tiempo real).

## Stack Tecnológico

* **Frameworks:** FastAPI (Python), React (TypeScript)
* **ORM & Base de Datos:** SQLModel, PostgreSQL
* **Autenticación:** OAuth2 con PyJWT (Hashed passwords con SHA-256)
* **Testing & CI/CD:** Pytest (98% de cobertura) y GitHub Actions con base de datos de prueba en la nube.
* **Integraciones:** Consumo de APIs REST asíncronas con `httpx`.

## Instalación y Ejecución Local

### 1. **Clonar el repositorio y entrar a la carpeta:**
 ```bash
 git clone <URL_DEL_REPOSITORIO>
 cd backend
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
```

### 4. ***Variables de Entorno:**
Crea un archivo .env en la raíz de backend/ con tus credenciales locales:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5432/suscripciones_db
SECRET_KEY=clave_secreta_super_segura_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. **Iniciar la aplicación:**
```bash
uvicorn main:app --reload
```
La API quedará disponible en http://127.0.0.1:8000.
