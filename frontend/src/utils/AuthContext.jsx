import { useState } from "react";
import { iniciarSesion, obtenerPerfil } from "../services/Auth.service";
import { AuthContext } from "./AuthProvider";

function usuarioGuardado() {
  try {
    return JSON.parse(localStorage.getItem("usuario") || "null");
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(usuarioGuardado);

  const login = async (email, password) => {
    const { access_token: token } = await iniciarSesion(email, password);
    const perfil = await obtenerPerfil(token);
    const userData = { email: perfil.email, role: perfil.rol };

    localStorage.setItem("token", token);
    localStorage.setItem("usuario", JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
	);
}
