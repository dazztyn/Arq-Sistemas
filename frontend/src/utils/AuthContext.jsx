import { useCallback, useState } from "react";
import { iniciarSesion, obtenerPerfil } from "../services/Auth.service";
import { AuthContext } from "./AuthProvider";

// El token y el usuario viven en localStorage para sobrevivir a un F5, pero la
// fuente de verdad mientras la app corre es el estado de React: así, al cerrar
// sesión, todos los componentes se enteran en el mismo render.
function usuarioGuardado() {
  try {
    return JSON.parse(localStorage.getItem("usuario") || "null");
  } catch {
    return null;
  }
}

function tokenGuardado() {
  return localStorage.getItem("token") || "";
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(usuarioGuardado);
  const [token, setToken] = useState(tokenGuardado);

  const login = async (email, password) => {
    const { access_token: nuevoToken } = await iniciarSesion(email, password);
    const perfil = await obtenerPerfil(nuevoToken);
    const userData = {
      id: perfil.id,
      nombre: perfil.nombre,
      email: perfil.email,
      role: perfil.rol,
    };

    localStorage.setItem("token", nuevoToken);
    localStorage.setItem("usuario", JSON.stringify(userData));
    setToken(nuevoToken);
    setUser(userData);
  };

  // useCallback porque el hook de suscripciones la usa como dependencia de un
  // efecto: si cambiara de identidad en cada render, recargaría en bucle.
  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setToken("");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
