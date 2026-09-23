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
  moneda: string;
  gasto_total_mensual: number;
}

const API_URL = import.meta.env.VITE_API_URL;

export const initialSubscriptions = [];

async function obtenerError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    return typeof data.detail === "string"
      ? data.detail
      : "No se pudo completar la solicitud.";
  } catch {
    return "No se pudo completar la solicitud.";
  }
}

async function solicitar<T>(ruta: string, token: string, opciones: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...opciones.headers,
    },
  });

  if (!response.ok) throw new Error(await obtenerError(response));
  return response.json();
}

export function listarSuscripciones(token: string): Promise<SuscripcionApi[]> {
  return solicitar<SuscripcionApi[]>("/api/suscripciones/listar", token);
}

export function obtenerResumen(token: string): Promise<ResumenApi> {
  return solicitar<ResumenApi>("/api/suscripciones/resumen?moneda=CLP", token);
}

export function convertirAMoneda(monto: number, origen: string, destino = "CLP") {
  const parametros = new URLSearchParams({
    monto: String(monto),
    origen,
    destino,
  });

  return fetch(`${API_URL}/api/conversion/?${parametros}`).then(async (response) => {
    if (!response.ok) throw new Error(await obtenerError(response));
    return response.json() as Promise<{ monto_convertido: number }>;
  });
}

export function crearSuscripcion(token: string, datos: {
  nombre_servicio: string;
  monto_original: number;
  moneda_original: string;
  fecha_proximo_cobro: string;
  periodicidad: "mensual" | "anual";
}) {
  return solicitar("/api/suscripciones/", token, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function desactivarSuscripcion(token: string, id: number) {
  return solicitar(`/api/suscripciones/${id}/desactivar`, token, { method: "PATCH" });
}

