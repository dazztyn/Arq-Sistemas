export interface SuscripcionApi {
  id: number;
  nombre_servicio: string;
  monto_original: number;
  moneda_original: string;
  fecha_proximo_cobro: string;
  activa: boolean;
  periodicidad: "mensual" | "anual";
}

export interface ResumenApi {
  usuario: string;
  moneda: string;
  gasto_total_mensual: number;
}

export interface AlertaApi {
  suscripcion_id: number;
  nombre_servicio: string;
  monto_original: number;
  moneda_original: string;
  // null cuando la API de divisas falló: el backend prefiere entregar la alerta
  // sin el monto convertido antes que no avisar del cobro
  monto_convertido: number | null;
  fecha_proximo_cobro: string;
  periodicidad: "mensual" | "anual";
  dias_restantes: number;
  vencida: boolean;
}

export interface AlertasApi {
  dias_ventana: number;
  moneda: string;
  total_alertas: number;
  alertas: AlertaApi[];
}

export interface DatosSuscripcion {
  nombre_servicio: string;
  monto_original: number;
  moneda_original: string;
  fecha_proximo_cobro: string;
  periodicidad: "mensual" | "anual";
}

// Sin el fallback, si falta el .env las llamadas van a "undefined/api/..." y fallan
// sin ningún mensaje que explique qué pasó.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/** El token expiró o no es válido. La UI la usa para cerrar sesión y redirigir. */
export class SesionExpirada extends Error {
  constructor() {
    super("Tu sesión expiró. Vuelve a iniciar sesión.");
    this.name = "SesionExpirada";
  }
}

async function obtenerError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    // FastAPI devuelve un array de errores en los 422 de validación
    if (Array.isArray(data.detail)) {
      return data.detail.map((error: { msg: string }) => error.msg).join(". ");
    }
    return typeof data.detail === "string"
      ? data.detail
      : "No se pudo completar la solicitud.";
  } catch {
    return "No se pudo completar la solicitud.";
  }
}

async function solicitar<T>(ruta: string, token: string, opciones: RequestInit = {}): Promise<T> {
  const cabeceras: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    ...(opciones.headers as Record<string, string>),
  };

  // Solo se declara el tipo de contenido cuando efectivamente se manda un body:
  // los PATCH de estado no envían nada.
  if (opciones.body) cabeceras["Content-Type"] = "application/json";

  const response = await fetch(`${API_URL}${ruta}`, { ...opciones, headers: cabeceras });

  // El 401 se distingue del resto para que la app pueda cerrar la sesión en vez de
  // mostrar un error suelto que el usuario no sabe cómo resolver.
  if (response.status === 401) throw new SesionExpirada();
  if (!response.ok) throw new Error(await obtenerError(response));

  return response.json();
}

export function listarSuscripciones(token: string): Promise<SuscripcionApi[]> {
  return solicitar<SuscripcionApi[]>("/api/suscripciones/listar", token);
}

export function obtenerResumen(token: string, moneda = "CLP"): Promise<ResumenApi> {
  return solicitar<ResumenApi>(`/api/suscripciones/resumen?moneda=${moneda}`, token);
}

export function obtenerAlertas(token: string, dias = 7, moneda = "CLP"): Promise<AlertasApi> {
  return solicitar<AlertasApi>(`/api/alertas/proximas?dias=${dias}&moneda=${moneda}`, token);
}

export function crearSuscripcion(token: string, datos: DatosSuscripcion) {
  return solicitar("/api/suscripciones/", token, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function actualizarSuscripcion(token: string, id: number, datos: DatosSuscripcion) {
  return solicitar(`/api/suscripciones/${id}`, token, {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}

export function desactivarSuscripcion(token: string, id: number) {
  return solicitar(`/api/suscripciones/${id}/desactivar`, token, { method: "PATCH" });
}

export function reactivarSuscripcion(token: string, id: number) {
  return solicitar(`/api/suscripciones/${id}/reactivar`, token, { method: "PATCH" });
}

export function renovarSuscripcion(token: string, id: number) {
  return solicitar(`/api/suscripciones/${id}/renovar`, token, { method: "PATCH" });
}

/**
 * Devuelve cuántas unidades de `destino` vale 1 de `origen`.
 *
 * Se pide con un monto base alto y se divide, en vez de pedir directamente por 1,
 * porque el backend redondea a 2 decimales: con monto=1 una moneda de tasa chica
 * (COP -> CLP ≈ 0,23) quedaría con solo dos cifras significativas.
 */
const MONTO_BASE = 100000;

export async function obtenerTasa(origen: string, destino = "CLP"): Promise<number> {
  if (origen === destino) return 1;

  const parametros = new URLSearchParams({
    monto: String(MONTO_BASE),
    origen,
    destino,
  });

  const response = await fetch(`${API_URL}/api/conversion/?${parametros}`);
  if (!response.ok) throw new Error(await obtenerError(response));

  const datos = (await response.json()) as { monto_convertido: number };
  return datos.monto_convertido / MONTO_BASE;
}
