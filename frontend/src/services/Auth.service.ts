interface RegistroUsuario {
	nombre: string;
	email: string;
	contrasena: string;
}

interface RespuestaError {
	detail?: string | Array<{ msg: string }>;
}

interface RespuestaLogin {
	access_token: string;
	token_type: string;
}

interface PerfilUsuario {
	id: number;
	nombre: string;
	email: string;
	rol: string;
}

// Mismo fallback que en Subscripciones.service: sin él, un .env ausente produce
// llamadas a "undefined/api/..." que fallan sin explicar la causa.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function obtenerError(response: Response): Promise<string> {
	try {
		const data = (await response.json()) as RespuestaError;
		if (Array.isArray(data.detail)) {
			return data.detail.map((error) => error.msg).join(". ");
		}
		return typeof data.detail === "string"
			? data.detail
			: "No se pudo completar la solicitud.";
	} catch {
		return "No se pudo completar la solicitud.";
	}
}

export async function registrarUsuario({
	nombre,
	email,
	contrasena,
}: RegistroUsuario): Promise<unknown> {
	const response = await fetch(`${API_URL}/api/usuarios/`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ nombre, email, contrasena }),
	});

	if (!response.ok) {
		throw new Error(await obtenerError(response));
	}

	return response.json();
}

export async function iniciarSesion(
	email: string,
	contrasena: string,
): Promise<RespuestaLogin> {
	const body = new URLSearchParams({ username: email, password: contrasena });
	const response = await fetch(`${API_URL}/api/usuarios/login`, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body,
	});

	if (!response.ok) {
		throw new Error(await obtenerError(response));
	}

	return response.json();
}

export async function obtenerPerfil(token: string): Promise<PerfilUsuario> {
	const response = await fetch(`${API_URL}/api/usuarios/perfil`, {
		headers: { Authorization: `Bearer ${token}` },
	});

	if (!response.ok) {
		throw new Error(await obtenerError(response));
	}

	return response.json();
}
