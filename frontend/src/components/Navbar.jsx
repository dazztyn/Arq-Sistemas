import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../utils/useAuth";

const contactEmail = "contacto@arqsistemas.com";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [toast, setToast] = useState("");

  const navItems = [
  { to: "/", label: "Inicio" },
  ];

  if (user) {
    navItems.push({ to: "/dashboard", label: "Dashboard" })
  }

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleCopyEmail = async (e) => {
    e.preventDefault();

    try {
      await navigator.clipboard.writeText(contactEmail);
      setToast("Correo copiado al portapapeles");
      setTimeout(() => setToast(""), 2000);
    } catch (error) {
      console.error("No se pudo copiar el correo:", error);
    }
  };

  return (
    <>
      {toast && (
        <div className="fixed left-1/2 top-16 z-60 -translate-x-1/2 rounded-md bg-secundario px-4 py-2 text-md font-medium text-texto">
          {toast}
        </div>
      )}

      <header className="sticky top-0 z-50 bg-fondo backdrop-blur-md">
        <div className="mx-auto flex items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <NavLink
            to="/"
            className="text-xl font-bold tracking-wide text-texto"
          >
            Placeholder<span className="text-primario">.</span>
          </NavLink>

          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `text-lg font-bold transition ${
                    isActive ? "text-texto" : "text-texto-dim hover:text-primario"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
            <a
              href={`mailto:${contactEmail}`}
              onClick={handleCopyEmail}
              className="text-lg font-bold text-texto-dim transition hover:text-primario"
            >
              Contacto
            </a>
          </nav>
          {user ? (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full bg-primario/70 px-4 py-2 text-lg font-semibold text-fondo transition hover:bg-primario"
            >
              Cerrar sesión
            </button>
          ) : (
            <NavLink
              to="/login"
              className="rounded-full bg-acento px-4 py-2 text-lg font-semibold text-fondo transition hover:bg-primario"
            >
              Iniciar sesión
            </NavLink>
          )}
        </div>
      </header>
    </>
  );
}

export default Navbar;