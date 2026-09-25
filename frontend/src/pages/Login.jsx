import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../utils/useAuth";

function Login() {
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // Cuando el token expira, el hook redirige acá con el motivo: sin esto el
  // usuario volvería al login sin saber por qué lo sacaron.
  const [error, setError] = useState(location.state?.mensaje || "");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Debes ingresar correo y contraseña.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("El correo no es válido.");
      return;
    }

    setError("");
    setIsLoading(true);
    login(email, password)
      .then(() => navigate("/dashboard"))
      .catch((requestError) => setError(requestError.message))
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-fondo px-4">
      <div className="w-full max-w-md bg-secundario/80 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-center text-texto mb-6">
          Iniciar sesión
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-texto mb-1">
              Correo
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="correo@ejemplo.com"
              className="w-full px-3 py-2 border border-texto text-texto rounded-sm focus:outline-none focus:ring-2 focus:ring-fondo"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-texto mb-1">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="********"
              className="w-full px-3 py-2 border border-texto text-texto rounded-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {error && (
            <p className="text-sm text-red-500 bg-red-50 rounded-md p-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="w-full bg-primario text-fondo font-semibold py-2.5 rounded-lg hover:shadow-lg hover:shadow-acento hover:-translate-y-0.5 transition"
          >
            {isLoading ? "Ingresando..." : "Entrar"}
          </button>

          <p className="text-center text-sm text-texto">
            ¿No tienes cuenta?{" "}
            <Link to="/register" className="text-primario font-medium hover:underline">
              Registrate
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login