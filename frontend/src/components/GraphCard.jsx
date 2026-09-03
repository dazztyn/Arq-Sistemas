import { useMemo } from "react"

function GraphCard({subscriptions}) {

  const categoryTotals = useMemo(() => {
      const totals = {};
      subscriptions.forEach((item) => {
        totals[item.category] = (totals[item.category] || 0) + Number(item.amount || 0);
      });
      return Object.entries(totals).map(([name, value]) => ({ name, value }));
    }, [subscriptions]);

  const maxCategoryValue = Math.max(...categoryTotals.map((item) => item.value), 1);

  const totalValue = categoryTotals.reduce(
    (total, category) => total + category.value,
    0
  );

  const colors = [
    "bg-emerald-500",
    "bg-sky-400",
    "bg-amber-400",
    "bg-rose-400",
    "bg-violet-400",
  ];

  return (
    <div className="rounded-2xl bg-secundario/50 p-5 shadow-lg">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-texto">
          Distribución por categorías
        </h3>
        <span className="text-sm text-texto-dim">Este mes</span>
      </div>

      <div className="flex h-64 items-end justify-center rounded-xl p-4">
        <div className="flex h-full w-28 flex-col-reverse overflow-hidden">
          {categoryTotals.map((category, index) => (
            <div
              key={category.name}
              className={`w-full border-t-2 rounded-md border-secundario ${
                colors[index % colors.length]
              }`}
              style={{
                height: totalValue
                  ? `${(category.value / totalValue) * 100}%`
                  : "0%",
              }}
              title={`${category.name}: ${category.value}`}
            />
          ))}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap justify-center gap-3">
        {categoryTotals.map((category, index) => (
          <div
            key={category.name}
            className="flex items-center gap-2 text-xs text-texto"
          >
            <span
              className={`h-3 w-3 rounded-sm ${
                colors[index % colors.length]
              }`}
            />
            <span>{category.name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default GraphCard