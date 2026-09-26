function FormularioSuscripcion({
  form,
  handleChange,
  handleSubmit,
  resetForm,
}) {

  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-texto">
          Gestor de suscripciones
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-texto">
            Nombre del servicio
          </label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Ej: Spotify"
            className="w-full rounded-xl bg-fondo px-3 py-2 text-texto outline-none ring-0 placeholder:text-texto-dim focus:border-emerald-500"
            required
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-texto">Monto</label>
            <input
              type="number"
              min="0"
              step="0.01"
              name="amount"
              value={form.amount}
              onChange={handleChange}
              placeholder="99"
              className="w-full rounded-xl bg-fondo px-3 py-2 text-texto outline-none focus:border-emerald-500"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-texto">Divisa</label>
            <select
              name="currency"
              value={form.currency}
              onChange={handleChange}
              className="w-full rounded-xl bg-fondo px-3 py-2 text-texto outline-none focus:border-emerald-500"
            >
              <option value="CLP">CLP</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="COP">COP</option>
              <option value="MXN">MXN</option>
            </select>
          </div>
        </div>

        <div>
          <div>
            <label className="mb-1 block text-sm text-texto">
              Frecuencia de cobro
            </label>
            {/* Solo las dos periodicidades que soporta la API. Antes había cuatro
                y las otras dos se guardaban como "mensual" sin avisar al usuario. */}
            <select
              name="frequency"
              value={form.frequency}
              onChange={handleChange}
              className="w-full rounded-xl bg-fondo px-3 py-2 text-texto outline-none focus:border-emerald-500"
            >
              <option value="Mensual">Mensual</option>
              <option value="Anual">Anual</option>
            </select>
          </div>
        </div>

        <div>
          {/* Fecha completa, no solo el día: el backend guarda la fecha exacta del
              próximo cobro, y con un día suelto se perdía el mes al editar. */}
          <label className="mb-1 block text-sm text-texto">
            Próxima fecha de cobro
          </label>
          <input
            type="date"
            name="fecha"
            value={form.fecha}
            onChange={handleChange}
            className="w-full rounded-xl bg-fondo px-3 py-2 text-texto outline-none focus:border-emerald-500"
            required
          />
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
              onClick={resetForm}
              className="rounded-xl bg-slate-800 px-4 py-2 font-semibold text-slate-200 transition hover:bg-slate-700"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

export default FormularioSuscripcion