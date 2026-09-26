function formatearMonto(valor, moneda = "CLP") {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: moneda,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(valor);
}

function textoDias(item) {
  if (item.vencida) {
    const dias = Math.abs(item.diffDays);
    return dias === 1 ? "Venció ayer" : `Venció hace ${dias} días`;
  }
  if (item.diffDays === 0) return "Hoy";
  return item.diffDays === 1 ? "Mañana" : `En ${item.diffDays} días`;
}

function ProximosCobros({
  upcomingCharges,
  totalVentana = 0,
  ventanaParcial = false,
  diasAlerta = 7,
  renovarCobro,
}) {
  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-texto">
          Próximos cobros
        </h3>
        <span className="rounded-full bg-acento/10 px-2 py-1 text-xs text-acento">
          ±{diasAlerta} días
        </span>
      </div>

      <div className="space-y-3">
        {upcomingCharges.length === 0 ? (
          <div className="rounded-xl p-4 text-sm text-texto-dim">
            No hay cobros en los próximos {diasAlerta} días.
          </div>
        ) : (
          upcomingCharges.map((item) => (
            <div
              key={item.id}
              className={`rounded-xl p-3 ${
                item.vencida
                  ? "bg-red-500/10 ring-1 ring-red-400/30"
                  : "bg-secundario/30"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-texto">{item.name}</p>
                  <p className="text-xs text-texto-dim">
                    {item.nextDate.toLocaleDateString("es-CL", {
                      day: "numeric",
                      month: "short",
                    })}
                  </p>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${item.vencida ? "text-red-300" : "text-acento"}`}>
                    {formatearMonto(item.amount, item.currency)}
                  </p>
                  <p className="text-xs text-texto-dim">{textoDias(item)}</p>
                </div>
              </div>

              {/* Cierra el ciclo del MVP: tras el cobro, la suscripción se pone al
                  día y sale de la lista. Sin esto, una vencida queda para siempre. */}
              <button
                type="button"
                onClick={() => renovarCobro(item.id)}
                className="mt-3 w-full rounded-lg bg-primario/20 px-3 py-1.5 text-xs font-semibold text-primario transition hover:bg-primario/30"
              >
                Ya me cobraron
              </button>
            </div>
          ))
        )}
      </div>

      {/* El total suma exactamente los cobros listados arriba, a monto completo.
          No se muestra con la lista vacía: ahí ya está el mensaje correspondiente. */}
      {upcomingCharges.length > 0 && (
        <div className="mt-5 border-t border-texto-dim/20 pt-4">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-texto">Total del período</span>
            <span className="text-xl font-bold text-primario">
              {formatearMonto(totalVentana)}
            </span>
          </div>
          {ventanaParcial && (
            <p className="mt-1 text-right text-xs text-texto-dim">
              no incluye los cobros sin conversión
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default ProximosCobros
