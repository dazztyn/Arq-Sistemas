import { useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import CifraCard from "../components/CifraCard";
import GraphCard from "../components/GraphCard";
import { initialSubscriptions } from "../services/Subscripciones.service";

const initialForm = {
  id: null,
  name: "",
  amount: "",
  currency: "USD",
  category: "Entretenimiento",
  frequency: "Mensual",
  billingDay: "1",
  isActive: true,
};

const categorias = [
  "Entretenimiento",
  "Productividad",
  "Salud",
  "Hogar",
  "Tecnología",
  "Transporte",
];

const getNextBillingDate = (billingDay, today) => {
  const nextDate = new Date(today.getFullYear(), today.getMonth(), billingDay);
  if (nextDate < today) {
    return new Date(today.getFullYear(), today.getMonth() + 1, billingDay);
  }
  return nextDate;
};

function Dashboard() {
  const [subscriptions, setSubscriptions] = useState(initialSubscriptions);
  const [form, setForm] = useState(initialForm);

  const monthlyBudget = 4200;
  const today = new Date();

  const activeSubscriptions = subscriptions.filter((item) => item.isActive);

  const totalMonthlySpend = useMemo(
    () =>
      activeSubscriptions.reduce((sum, item) => sum + Number(item.amount || 0), 0),
    [activeSubscriptions]
  );

  const remainingBudget = monthlyBudget - totalMonthlySpend;

  const upcomingCharges = useMemo(() => {
    return activeSubscriptions
      .map((subscription) => {
        const date = getNextBillingDate(subscription.billingDay, today);
        const diffDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
        return {
          ...subscription,
          nextDate: date,
          diffDays,
        };
      })
      .filter((item) => item.diffDays >= 0 && item.diffDays <= 5)
      .sort((a, b) => a.diffDays - b.diffDays);
  }, [activeSubscriptions, today]);

  const projectedSpend = Math.round(
    totalMonthlySpend +
      upcomingCharges.reduce((sum, item) => sum + Number(item.amount || 0), 0) * 0.75
  );

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    const newSubscription = {
      id: form.id ?? Date.now(),
      name: form.name.trim(),
      amount: Number(form.amount),
      currency: form.currency,
      category: form.category,
      frequency: form.frequency,
      billingDay: Number(form.billingDay),
      isActive: form.isActive,
    };

    setSubscriptions((current) => {
      if (form.id) {
        return current.map((item) =>
          item.id === form.id ? newSubscription : item
        );
      }
      return [...current, newSubscription];
    });

    setForm(initialForm);
  };

  const handleEdit = (item) => {
    setForm({
      id: item.id,
      name: item.name,
      amount: String(item.amount),
      currency: item.currency,
      category: item.category,
      frequency: item.frequency,
      billingDay: String(item.billingDay),
      isActive: item.isActive,
    });
  };

  const toggleSubscription = (id) => {
    setSubscriptions((current) =>
      current.map((item) =>
        item.id === id ? { ...item, isActive: !item.isActive } : item
      )
    );
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-fondo text-texto">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <header className="mb-8 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="mt-1 text-3xl font-bold text-texto">
                Dashboard de gastos
              </h1>
            </div>
          </header>

          <section className="grid gap-4 md:grid-cols-3">
            <CifraCard texto="Gasto total del mes" numero={totalMonthlySpend} />
            <CifraCard texto="Presupuesto restante" numero={remainingBudget} />
            <CifraCard texto="Gasto proyectado" numero={projectedSpend} />
          </section>

          <section className="mt-8 grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
            <GraphCard subscriptions={activeSubscriptions}/>

            <div className="rounded-2xl bg-secundario/50 p-5 shadow-lg">
              <div className="mb-5 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-texto">
                  Próximos cobros
                </h3>
                <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">
                  5 días
                </span>
              </div>

              <div className="space-y-3">
                {upcomingCharges.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-slate-700 p-4 text-sm text-slate-400">
                    No hay cobros en los próximos 5 días.
                  </div>
                ) : (
                  upcomingCharges.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between rounded-xl border border-slate-800 bg-primario/30 p-3"
                    >
                      <div>
                        <p className="font-medium text-texto">{item.name}</p>
                        <p className="text-xs text-slate-400">
                          {item.nextDate.toLocaleDateString("es-ES", {
                            day: "numeric",
                            month: "short",
                          })}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-emerald-300">
                          {item.amount} {item.currency}
                        </p>
                        <p className="text-xs text-slate-400">
                          {item.diffDays === 0 ? "Hoy" : `En ${item.diffDays} días`}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>

          <section className="mt-8 grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
            <div className="rounded-2xl bg-secundario/50 p-5 shadow-lg">
              <div className="mb-5">
                <h3 className="text-lg font-semibold text-texto">
                  Gestor de suscripciones
                </h3>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm text-slate-300">
                    Nombre del servicio
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Ej: Spotify"
                    className="w-full rounded-xl bg-slate-950 px-3 py-2 text-texto outline-none ring-0 placeholder:text-slate-500 focus:border-emerald-500"
                    required
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm text-slate-300">Monto</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      name="amount"
                      value={form.amount}
                      onChange={handleChange}
                      placeholder="99"
                      className="w-full rounded-xl bg-slate-950 px-3 py-2 text-texto outline-none focus:border-emerald-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm text-slate-300">Divisa</label>
                    <select
                      name="currency"
                      value={form.currency}
                      onChange={handleChange}
                      className="w-full rounded-xl bg-slate-950 px-3 py-2 text-texto outline-none focus:border-emerald-500"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="COP">COP</option>
                      <option value="MXN">MXN</option>
                    </select>
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm text-slate-300">Categoría</label>
                    <select
                      name="category"
                      value={form.category}
                      onChange={handleChange}
                      className="w-full rounded-xl bg-slate-950 px-3 py-2 text-texto outline-none focus:border-emerald-500"
                    >
                      {categorias.map((category) => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="mb-1 block text-sm text-slate-300">
                      Frecuencia de cobro
                    </label>
                    <select
                      name="frequency"
                      value={form.frequency}
                      onChange={handleChange}
                      className="w-full rounded-xl bg-acento/50 px-3 py-2 text-texto outline-none focus:border-emerald-500"
                    >
                      <option value="Mensual">Mensual</option>
                      <option value="Trimestral">Trimestral</option>
                      <option value="Anual">Anual</option>
                      <option value="Quincenal">Quincenal</option>
                    </select>
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm text-slate-300">
                      Día de facturación
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="31"
                      name="billingDay"
                      value={form.billingDay}
                      onChange={handleChange}
                      className="w-full rounded-xl bg-slate-950 px-3 py-2 text-texto outline-none focus:border-emerald-500"
                      required
                    />
                  </div>

                  <div className="flex items-end">
                    <label className="flex w-full cursor-pointer items-center justify-between rounded-xl  bg-slate-950 px-3 py-2">
                      <span className="text-sm text-slate-300">
                        Suscripción activa
                      </span>
                      <input
                        type="checkbox"
                        name="isActive"
                        checked={form.isActive}
                        onChange={handleChange}
                        className="h-5 w-5 accent-emerald-500"
                      />
                    </label>
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    className="flex-1 rounded-xl bg-primario/70 px-4 py-2 font-semibold text-slate-950 transition hover:bg-primario"
                  >
                    {form.id ? "Guardar cambios" : "Agregar suscripción"}
                  </button>

                  {form.id && (
                    <button
                      type="button"
                      onClick={() => setForm(initialForm)}
                      className="rounded-xl bg-slate-800 px-4 py-2 font-semibold text-slate-200 transition hover:bg-slate-700"
                    >
                      Cancelar
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="rounded-2xl bg-secundario/50 p-5 shadow-lg">
              <div className="mb-5 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-texto">
                  Suscripciones registradas
                </h3>
                <span className="text-sm text-slate-400">
                  {subscriptions.length} servicios
                </span>
              </div>

              <div className="space-y-3">
                {subscriptions.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-xl bg-primario/25 p-3"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-texto">{item.name}</p>
                        <p className="text-xs text-texto-dim">
                          {item.category} • {item.frequency} • Día {item.billingDay}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="font-semibold text-slate-100">
                          {item.amount} {item.currency}
                        </p>
                        <p
                          className={`text-xs ${
                            item.isActive ? "text-acento" : "text-red-300"
                          }`}
                        >
                          {item.isActive ? "Activa" : "Desactivada"}
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between gap-2">
                      <button
                        type="button"
                        onClick={() => handleEdit(item)}
                        className="rounded-lg  px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800"
                      >
                        Editar
                      </button>

                      <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                        <span>Desactivar</span>
                        <input
                          type="checkbox"
                          checked={!item.isActive}
                          onChange={() => toggleSubscription(item.id)}
                          className="h-4 w-4 accent-red-500"
                        />
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </div>
    </>
  );
}

export default Dashboard;