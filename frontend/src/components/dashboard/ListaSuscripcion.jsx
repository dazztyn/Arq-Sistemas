function ListaSuscripcion({ subscriptions, handleEdit, toggleSubscription }) {

  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-texto">
          Suscripciones registradas
        </h3>
        <span className="text-sm text-texto-dim">
          {subscriptions.length} servicios
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {subscriptions.map((item) => (
          <div
            key={item.id}
            className="rounded-xl bg-secundario/30 p-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-bold text-texto">{item.name}</p>
                <p className="text-xs text-texto-dim">
                  {item.frequency} • {item.nextBillingDate.toLocaleDateString("es-CL", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
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

              {/* La etiqueta sigue al estado: antes decía siempre "Desactivar"
                  aunque la suscripción ya estuviera desactivada. */}
              <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-texto">
                <span>{item.isActive ? "Desactivar" : "Reactivar"}</span>
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
  )
}

export default ListaSuscripcion