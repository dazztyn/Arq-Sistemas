"""Prueba de humo de la API: recorre los 13 endpoints de punta a punta.

Complementa a pytest, no lo reemplaza: pytest levanta la app en memoria, esto
golpea un servidor de verdad por HTTP. Sirve igual contra localhost que contra
la URL pública de Railway, así que es la forma rápida de confirmar que un
despliegue quedó bien.

Solo usa la biblioteca estándar, así que corre con cualquier Python 3 sin
instalar nada.

    python scripts/probar_endpoints.py
    python scripts/probar_endpoints.py https://mi-backend.up.railway.app
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")

# Se acumulan para el resumen final en vez de cortar en la primera falla:
# interesa ver todo lo que está roto de una pasada, no solo lo primero.
fallas = []
avisos = []


def pedir(metodo, ruta, token=None, json_body=None, form_body=None):
    """Devuelve (status, cuerpo_parseado). No lanza en los 4xx/5xx."""
    datos = None
    cabeceras = {}

    if json_body is not None:
        datos = json.dumps(json_body).encode()
        cabeceras["Content-Type"] = "application/json"
    elif form_body is not None:
        datos = urllib.parse.urlencode(form_body).encode()
        cabeceras["Content-Type"] = "application/x-www-form-urlencoded"

    if token:
        cabeceras["Authorization"] = f"Bearer {token}"

    peticion = urllib.request.Request(f"{BASE}{ruta}", data=datos, headers=cabeceras, method=metodo)

    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            return respuesta.status, json.loads(respuesta.read() or b"null")
    except urllib.error.HTTPError as error:
        cuerpo = error.read()
        try:
            return error.code, json.loads(cuerpo or b"null")
        except json.JSONDecodeError:
            return error.code, cuerpo.decode(errors="replace")
    except urllib.error.URLError as error:
        print(f"\n  No se pudo conectar con {BASE} — ¿está corriendo el backend?\n  ({error.reason})")
        sys.exit(2)


def revisar(descripcion, condicion, detalle=""):
    print(f"  {'ok  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion + (f" → {detalle}" if detalle else ""))
    return condicion


def titulo(texto):
    print(f"\n{texto}")


# ─────────────────────────────────────────────────────────────────────────────
print(f"Probando {BASE}")

titulo("1. Estado del servicio")
estado, _ = pedir("GET", "/")
revisar("GET / responde 200", estado == 200, f"status {estado}")

titulo("2. Registro y login")
email = f"prueba_{int(time.time() * 1000)}@test.com"
CONTRASENA = "clave-de-prueba"

estado, registro = pedir("POST", "/api/usuarios/", json_body={
    "nombre": "Usuario de Prueba", "email": email, "contrasena": CONTRASENA,
})
revisar("POST /api/usuarios/ crea el usuario", estado == 200, f"status {estado}")

estado, _ = pedir("POST", "/api/usuarios/", json_body={
    "nombre": "Repetido", "email": email, "contrasena": CONTRASENA,
})
revisar("el email duplicado da 400", estado == 400, f"status {estado}")

estado, sesion = pedir("POST", "/api/usuarios/login",
                       form_body={"username": email, "password": CONTRASENA})
revisar("POST /api/usuarios/login devuelve un token", estado == 200 and "access_token" in (sesion or {}))
token = (sesion or {}).get("access_token", "")

estado, _ = pedir("POST", "/api/usuarios/login",
                  form_body={"username": email, "password": "clave-incorrecta"})
revisar("la contraseña incorrecta da 401", estado == 401, f"status {estado}")

titulo("3. Perfil y control de acceso")
estado, perfil = pedir("GET", "/api/usuarios/perfil", token=token)
revisar("GET /api/usuarios/perfil responde 200", estado == 200, f"status {estado}")
revisar("el perfil trae id, nombre, email y rol",
        all(campo in (perfil or {}) for campo in ("id", "nombre", "email", "rol")),
        f"recibido: {perfil}")

estado, _ = pedir("GET", "/api/usuarios/perfil")
revisar("sin token da 401", estado == 401, f"status {estado}")

estado, _ = pedir("GET", "/api/usuarios/perfil", token="token.claramente.invalido")
revisar("con un token inventado da 401", estado == 401, f"status {estado}")

titulo("4. Crear suscripciones")
# Se usa CLP como moneda de origen y destino a propósito: así el backend se
# salta la API de divisas y la prueba no depende de un servicio de terceros.
EN_UNA_SEMANA = (date.today() + timedelta(days=5)).isoformat()

estado, mensual = pedir("POST", "/api/suscripciones/", token=token, json_body={
    "nombre_servicio": "Plan Mensual", "monto_original": 10000,
    "moneda_original": "CLP", "fecha_proximo_cobro": EN_UNA_SEMANA,
    "periodicidad": "mensual",
})
revisar("POST /api/suscripciones/ (mensual)", estado == 200, f"status {estado}")
id_mensual = (mensual or {}).get("suscripcion_id")

estado, anual = pedir("POST", "/api/suscripciones/", token=token, json_body={
    "nombre_servicio": "Plan Anual", "monto_original": 120000,
    "moneda_original": "CLP", "fecha_proximo_cobro": EN_UNA_SEMANA,
    "periodicidad": "anual",
})
revisar("POST /api/suscripciones/ (anual)", estado == 200, f"status {estado}")
id_anual = (anual or {}).get("suscripcion_id")

estado, _ = pedir("POST", "/api/suscripciones/", token=token, json_body={
    "nombre_servicio": "Periodicidad inventada", "monto_original": 1,
    "moneda_original": "CLP", "fecha_proximo_cobro": EN_UNA_SEMANA,
    "periodicidad": "cada_martes",
})
revisar("una periodicidad inválida da 422", estado == 422, f"status {estado}")

titulo("5. Listar y resumen")
estado, listado = pedir("GET", "/api/suscripciones/listar", token=token)
revisar("GET /listar devuelve las 2 suscripciones", estado == 200 and len(listado or []) == 2,
        f"status {estado}, {len(listado or [])} items")

estado, resumen = pedir("GET", "/api/suscripciones/resumen?moneda=CLP", token=token)
total = (resumen or {}).get("gasto_total_mensual")
# 10.000 mensual + 120.000 anual / 12 = 20.000
revisar("GET /resumen prorratea la anual a 1/12 (espera 20000)", total == 20000,
        f"recibido {total}")

titulo("6. Editar")
estado, _ = pedir("PUT", f"/api/suscripciones/{id_mensual}", token=token, json_body={
    "nombre_servicio": "Plan Mensual Editado", "monto_original": 15000,
    "moneda_original": "CLP", "fecha_proximo_cobro": EN_UNA_SEMANA,
    "periodicidad": "mensual",
})
revisar("PUT /api/suscripciones/{id} edita", estado == 200, f"status {estado}")

_, listado = pedir("GET", "/api/suscripciones/listar", token=token)
editada = next((s for s in (listado or []) if s["id"] == id_mensual), {})
revisar("el PUT aplicó los cambios", editada.get("monto_original") == 15000,
        f"monto {editada.get('monto_original')}")
revisar("el PUT NO tocó el campo activa", editada.get("activa") is True,
        f"activa {editada.get('activa')}")

titulo("7. Desactivar y reactivar")
estado, _ = pedir("PATCH", f"/api/suscripciones/{id_anual}/desactivar", token=token)
revisar("PATCH /desactivar", estado == 200, f"status {estado}")

_, resumen = pedir("GET", "/api/suscripciones/resumen?moneda=CLP", token=token)
revisar("el resumen excluye la desactivada (espera 15000)",
        (resumen or {}).get("gasto_total_mensual") == 15000,
        f"recibido {(resumen or {}).get('gasto_total_mensual')}")

_, listado = pedir("GET", "/api/suscripciones/listar", token=token)
revisar("/listar sí devuelve la desactivada (historial)", len(listado or []) == 2,
        f"{len(listado or [])} items")

estado, _ = pedir("PATCH", f"/api/suscripciones/{id_anual}/reactivar", token=token)
revisar("PATCH /reactivar", estado == 200, f"status {estado}")

titulo("8. Renovar")
_, listado = pedir("GET", "/api/suscripciones/listar", token=token)
antes = next(s["fecha_proximo_cobro"] for s in listado if s["id"] == id_mensual)
estado, renovada = pedir("PATCH", f"/api/suscripciones/{id_mensual}/renovar", token=token)
revisar("PATCH /renovar", estado == 200, f"status {estado}")
despues = (renovada or {}).get("fecha_proximo_cobro")
revisar("la fecha avanzó un ciclo", despues is not None and despues > antes,
        f"{antes} → {despues}")

titulo("9. Alertas")
estado, alertas = pedir("GET", "/api/alertas/proximas?dias=7&moneda=CLP", token=token)
revisar("GET /api/alertas/proximas responde 200", estado == 200, f"status {estado}")
lista = (alertas or {}).get("alertas", [])
revisar("la suscripción anual aparece en la ventana de 7 días",
        any(a["suscripcion_id"] == id_anual for a in lista),
        f"{len(lista)} alertas")
if lista:
    revisar("cada alerta trae dias_restantes y la marca de vencida",
            all("dias_restantes" in a and "vencida" in a for a in lista))

titulo("10. Aislamiento entre usuarios")
otro_email = f"intruso_{int(time.time() * 1000)}@test.com"
pedir("POST", "/api/usuarios/", json_body={
    "nombre": "Intruso", "email": otro_email, "contrasena": CONTRASENA,
})
_, otra_sesion = pedir("POST", "/api/usuarios/login",
                       form_body={"username": otro_email, "password": CONTRASENA})
otro_token = (otra_sesion or {}).get("access_token", "")

estado, ajenas = pedir("GET", "/api/suscripciones/listar", token=otro_token)
revisar("el otro usuario no ve suscripciones ajenas", len(ajenas or []) == 0,
        f"{len(ajenas or [])} items")

estado, _ = pedir("PATCH", f"/api/suscripciones/{id_mensual}/desactivar", token=otro_token)
revisar("desactivar una suscripción ajena da 404", estado == 404, f"status {estado}")

estado, _ = pedir("PUT", f"/api/suscripciones/{id_mensual}", token=otro_token, json_body={
    "nombre_servicio": "Secuestrada", "monto_original": 1, "moneda_original": "CLP",
    "fecha_proximo_cobro": EN_UNA_SEMANA, "periodicidad": "mensual",
})
revisar("editar una suscripción ajena da 404", estado == 404, f"status {estado}")

titulo("11. Conversión (depende de la API externa de divisas)")
estado, conversion = pedir("GET", "/api/conversion/?monto=100&origen=USD&destino=CLP")
if estado == 200 and isinstance((conversion or {}).get("monto_convertido"), (int, float)):
    print("  ok    GET /api/conversion/ convierte correctamente")
elif estado == 503:
    print("  aviso GET /api/conversion/ dio 503: la API de divisas no respondió")
    print("        (el backend lo manejó bien; es el servicio externo, no el código)")
    avisos.append("La API de divisas no respondió — reintenta con red disponible")
else:
    revisar("GET /api/conversion/ convierte", False, f"status {estado}, cuerpo {conversion}")

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "─" * 60)
if avisos:
    print(f"{len(avisos)} aviso(s):")
    for aviso in avisos:
        print(f"  · {aviso}")

if fallas:
    print(f"\n{len(fallas)} prueba(s) fallaron:")
    for falla in fallas:
        print(f"  · {falla}")
    sys.exit(1)

print("Todas las pruebas pasaron.")
