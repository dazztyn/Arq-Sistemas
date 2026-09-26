import { useMemo } from "react"

const colors = [
  "bg-emerald-500",
  "bg-sky-400",
  "bg-amber-400",
  "bg-rose-400",
  "bg-violet-400",
  ];

const formatAmount = (value, currency = "CLP") =>
  new Intl.NumberFormat("es-CL", {
    maximumFractionDigits: 0,
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
  }).format(value);

function GraphCard({ subscriptions = [] }) {
  const subscriptionTotals = useMemo(() => {
    return subscriptions
      .map((subscription) => ({
        id: subscription.id,
        name: subscription.name || "Suscripción sin nombre",
        value: Number(subscription.amountClp ?? subscription.amount ?? 0),
        originalValue: Number(subscription.amount || 0),
        currency: subscription.currency || "CLP",
      }))
      .sort((first, second) => second.value - first.value);
  }, [subscriptions]);

  const totalValue = subscriptionTotals.reduce((total, subscription) => total + subscription.value, 0);
  const getSubscriptionColor = (index) => colors[index % colors.length];

  return (
    <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-texto">Gastos por suscripción</h3>
          <p className="mt-1 text-sm text-texto-dim">Distribución de tus suscripciones activas por servicio</p>
        </div>
        <div className="shrink-0 text-right">
          <p className="text-2xl font-bold text-primario">{formatAmount(totalValue)}</p>
          <p className="text-xs text-texto-dim">total registrado</p>
        </div>
      </div>

      {subscriptionTotals.length === 0 ? (
        <div className="flex min-h-56 items-center justify-center rounded-xl border border-dashed border-texto-dim/30 px-6 text-center">
          <p className="max-w-xs text-sm text-texto-dim">
            Agrega una suscripción para ver cómo se distribuyen tus gastos.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          <div
            className="flex h-6 overflow-hidden rounded-full bg-fondo/80 ring-1 ring-white/5"
            role="img"
            aria-label="Distribución de gastos por categoría"
          >
            {subscriptionTotals.map((subscription, index) => (
              <div
                key={subscription.id}
                className={`h-full ${getSubscriptionColor(index)} transition-all duration-500 first:rounded-l-full last:rounded-r-full`}
                style={{ width: `${(subscription.value / totalValue) * 100}%` }}
                title={`${subscription.name}: ${formatAmount(subscription.originalValue, subscription.currency)} (${formatAmount(subscription.value)} convertidos)`}
              />
            ))}
          </div>

          <div className="grid gap-x-5 gap-y-3 sm:grid-cols-2">
            {subscriptionTotals.map((subscription, index) => (
              <div key={subscription.id} className="flex min-w-0 items-center justify-between gap-3 text-sm">
                <div className="flex min-w-0 items-center gap-2">
                  <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${getSubscriptionColor(index)}`} />
                  <span className="truncate text-texto">{subscription.name}</span>
                </div>
                <div className="flex shrink-0 items-center gap-2 text-right">
                  <span className="font-semibold text-texto">
                    {formatAmount(subscription.originalValue, subscription.currency)}
                  </span>
                  <span className="text-xs text-texto-dim">({formatAmount(subscription.value)})</span>
                  <span className="w-9 text-xs text-texto-dim">
                    {Math.round((subscription.value / totalValue) * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default GraphCard