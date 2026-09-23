function ProximosCobros({upcomingCharges}) {
  return(
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-texto">
          Próximos cobros
        </h3>
        <span className="rounded-full bg-acento/10 px-2 py-1 text-xs text-acento">
          5 días
        </span>
      </div>

      <div className="space-y-3">
        {upcomingCharges.length === 0 ? (
          <div className="rounded-xl p-4 text-sm text-texto-dim">
            No hay cobros en los próximos 5 días.
          </div>
        ) : (
          upcomingCharges.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl bg-secundario/30 p-3"
            >
              <div>
                <p className="font-medium text-texto">{item.name}</p>
                <p className="text-xs text-texto-dim">
                  {item.nextDate.toLocaleDateString("es-ES", {
                    day: "numeric",
                    month: "short",
                  })}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-acento">
                  {item.amount} {item.currency}
                </p>
                <p className="text-xs text-texto-dim">
                  {item.diffDays === 0 ? "Hoy" : `En ${item.diffDays} días`}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ProximosCobros