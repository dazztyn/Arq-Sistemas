import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  actualizarSuscripcion,
  crearSuscripcion,
  desactivarSuscripcion,
  listarSuscripciones,
  obtenerAlertas,
  obtenerResumen,
  obtenerTasa,
  reactivarSuscripcion,
  renovarSuscripcion,
  SesionExpirada,
} from "../services/Subscripciones.service";
import { useAuth } from "../utils/useAuth";

const MONEDA_BASE = "CLP";
const DIAS_ALERTA = 7;

export const initialForm = {
  id: null,
  name: "",
  amount: "",
  currency: MONEDA_BASE,
  frequency: "Mensual",
  // Fecha completa en formato YYYY-MM-DD, tal como la entrega un <input type="date">
  // y como la espera el backend. No se convierte a Date en el camino, así se evita
  // el desfase de un día que produce toISOString() según la zona horaria.
  fecha: "",
};

export function useSubscriptions() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const [subscriptions, setSubscriptions] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [totalMensual, setTotalMensual] = useState(0);
  const [form, setForm] = useState(initialForm);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Un token vencido no es un error más: no sirve reintentar ni mostrar el mensaje
  // suelto, hay que cerrar la sesión y mandar al login.
  const manejarError = useCallback(
    (fallo, mensajePorDefecto) => {
      if (fallo instanceof SesionExpirada) {
        logout();
        navigate("/login", { replace: true, state: { mensaje: fallo.message } });
        return;
      }
      setError(fallo.message || mensajePorDefecto);
    },
    [logout, navigate],
  );

  const cargarDatos = useCallback(async () => {
    if (!token) return;

    setIsLoading(true);
    setError("");

    try {
      // Las tres lecturas van en paralelo, pero con allSettled y no con all: el
      // resumen y las alertas dependen de la API externa de divisas, así que si
      // esa se cae, un Promise.all haría fallar también el listado, que no la
      // necesita, y el usuario se quedaría sin ver ninguna suscripción.
      const [resListado, resResumen, resAlertas] = await Promise.allSettled([
        listarSuscripciones(token),
        obtenerResumen(token, MONEDA_BASE),
        obtenerAlertas(token, DIAS_ALERTA, MONEDA_BASE),
      ]);

      // Un token vencido hace fallar las tres por igual: se atiende primero.
      const sesionCaida = [resListado, resResumen, resAlertas].find(
        (r) => r.status === "rejected" && r.reason instanceof SesionExpirada,
      );
      if (sesionCaida) {
        manejarError(sesionCaida.reason);
        return;
      }

      // El listado sí es imprescindible: sin él no hay nada que mostrar.
      if (resListado.status === "rejected") {
        setError(resListado.reason.message || "No se pudieron cargar las suscripciones.");
        return;
      }

      const datos = resListado.value;

      // Una tasa por moneda distinta, no una por suscripción: con 10 servicios en
      // USD antes se pedían 10 veces el mismo valor a la API de divisas.
      const monedas = [...new Set(datos.map((s) => s.moneda_original))];
      const tasas = {};
      await Promise.all(
        monedas.map(async (moneda) => {
          try {
            tasas[moneda] = await obtenerTasa(moneda, MONEDA_BASE);
          } catch {
            // Si la API externa falla, se muestra igual la suscripción sin el
            // monto convertido, en vez de dejar el dashboard en blanco.
            tasas[moneda] = null;
          }
        }),
      );

      setSubscriptions(datos.map((s) => adaptarSuscripcion(s, tasas[s.moneda_original])));
      // null, no 0: un cero se leería como "no gastas nada", que es distinto de
      // "no se pudo calcular". La tarjeta muestra un guion en ese caso.
      setTotalMensual(resResumen.status === "fulfilled" ? resResumen.value.gasto_total_mensual : null);
      setAlertas(resAlertas.status === "fulfilled" ? resAlertas.value.alertas.map(adaptarAlerta) : []);

      if (resResumen.status === "rejected" || resAlertas.status === "rejected") {
        setError("No se pudo contactar la API de divisas: el total y los próximos cobros pueden estar incompletos.");
      }
    } catch (fallo) {
      manejarError(fallo, "No se pudieron cargar las suscripciones.");
    } finally {
      setIsLoading(false);
    }
  }, [token, manejarError]);

  useEffect(() => {
    // queueMicrotask saca la actualización de estado del cuerpo del efecto:
    // llamar a cargarDatos() de forma síncrona dispara renders en cascada
    // (regla react-hooks/set-state-in-effect).
    queueMicrotask(cargarDatos);
  }, [cargarDatos]);

  const activeSubscriptions = useMemo(
    () => subscriptions.filter((s) => s.isActive),
    [subscriptions],
  );

  // Cuánto queda por pagar de aquí a fin de mes. Es una cifra distinta al total
  // mensual (que prorratea las anuales), no una partición de él.
  const pendienteEsteMes = useMemo(() => {
    const hoy = new Date();
    const desde = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
    const finDeMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);

    return Math.round(
      activeSubscriptions.reduce((total, s) => {
        const cobraEsteMes = s.nextBillingDate >= desde && s.nextBillingDate <= finDeMes;
        return cobraEsteMes ? total + Number(s.amountClp || 0) : total;
      }, 0),
    );
  }, [activeSubscriptions]);

  // Lo que se cobra dentro de la ventana de alertas, a monto completo. A diferencia
  // del gasto mensual, acá una anual entra por sus 120.000 y no por su doceava parte:
  // responde "cuánta plata sale de la cuenta estos días", no "cuánto cuesta al mes".
  // Suma todo lo que la tarjeta lista, incluidas las vencidas, para que el total
  // siempre cuadre con lo que el usuario tiene a la vista.
  const totalVentana = useMemo(
    () => Math.round(alertas.reduce((total, a) => total + Number(a.amountClp || 0), 0)),
    [alertas],
  );

  // El backend entrega la alerta con monto_convertido en null cuando la API de divisas
  // falla. Sin avisarlo, el total se vería completo cuando en realidad le falta un cobro.
  const ventanaParcial = useMemo(
    () => alertas.some((a) => a.amountClp == null),
    [alertas],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const resetForm = () => setForm(initialForm);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!token) return;

    const datos = {
      nombre_servicio: form.name.trim(),
      monto_original: Number(form.amount),
      moneda_original: form.currency,
      fecha_proximo_cobro: form.fecha,
      periodicidad: form.frequency === "Anual" ? "anual" : "mensual",
    };

    try {
      // Con id se edita, sin id se crea. Antes, el caso de edición salía con un
      // return silencioso y el botón "Guardar cambios" no hacía nada.
      if (form.id) {
        await actualizarSuscripcion(token, form.id, datos);
      } else {
        await crearSuscripcion(token, datos);
      }
      setForm(initialForm);
      await cargarDatos();
    } catch (fallo) {
      manejarError(fallo, "No se pudo guardar la suscripción.");
    }
  };

  const handleEdit = (item) => {
    setForm({
      id: item.id,
      name: item.name,
      amount: String(item.amount),
      currency: item.currency,
      frequency: item.frequency,
      fecha: item.fecha,
    });
  };

  // El backend tiene un endpoint por acción, así que acá se elige cuál según el
  // estado actual. Antes siempre llamaba a desactivar y no se podía reactivar.
  const toggleSubscription = async (id) => {
    const suscripcion = subscriptions.find((s) => s.id === id);
    if (!suscripcion) return;

    try {
      if (suscripcion.isActive) {
        await desactivarSuscripcion(token, id);
      } else {
        await reactivarSuscripcion(token, id);
      }
      await cargarDatos();
    } catch (fallo) {
      manejarError(fallo, "No se pudo cambiar el estado de la suscripción.");
    }
  };

  const renovarCobro = async (id) => {
    try {
      await renovarSuscripcion(token, id);
      await cargarDatos();
    } catch (fallo) {
      manejarError(fallo, "No se pudo renovar la suscripción.");
    }
  };

  return {
    subscriptions,
    activeSubscriptions,
    form,
    totalMonthlySpend: totalMensual,
    pendienteEsteMes,
    upcomingCharges: alertas,
    totalVentana,
    ventanaParcial,
    diasAlerta: DIAS_ALERTA,
    handleChange,
    handleSubmit,
    resetForm,
    handleEdit,
    toggleSubscription,
    renovarCobro,
    isLoading,
    error,
  };
}

/** Convierte "2026-09-28" en un Date a medianoche local, sin pasar por UTC. */
function aFechaLocal(texto) {
  return new Date(`${texto}T00:00:00`);
}

function adaptarSuscripcion(suscripcion, tasa) {
  return {
    id: suscripcion.id,
    name: suscripcion.nombre_servicio,
    amount: suscripcion.monto_original,
    currency: suscripcion.moneda_original,
    // null cuando no se pudo obtener la tasa; los componentes caen al monto original
    amountClp: tasa == null ? null : Math.round(suscripcion.monto_original * tasa),
    frequency: suscripcion.periodicidad === "anual" ? "Anual" : "Mensual",
    fecha: suscripcion.fecha_proximo_cobro,
    nextBillingDate: aFechaLocal(suscripcion.fecha_proximo_cobro),
    isActive: suscripcion.activa,
  };
}

function adaptarAlerta(alerta) {
  return {
    id: alerta.suscripcion_id,
    name: alerta.nombre_servicio,
    amount: alerta.monto_original,
    currency: alerta.moneda_original,
    amountClp: alerta.monto_convertido,
    nextDate: aFechaLocal(alerta.fecha_proximo_cobro),
    diffDays: alerta.dias_restantes,
    vencida: alerta.vencida,
  };
}
