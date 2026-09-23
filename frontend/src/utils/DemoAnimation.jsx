import { useEffect, useState } from "react"
const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))

function DemoAnimation() {
  const [service, setService] = useState("")
  const [amount, setAmount] = useState("")
  const [stage, setStage] = useState("service")
  const [added, setAdded] = useState(false)

  useEffect(() => {
    let cancelled = false

    const typeText = async (text, setter) => {
      for (const character of text) {
        if (cancelled) return
        setter((current) => current + character)
        await sleep(90 + Math.random() * 55)
      }
    }

    const runDemo = async () => {
      while (!cancelled) {
        setService("")
        setAmount("")
        setAdded(false)
        setStage("service")
        await sleep(450)
        await typeText("Netflix", setService)
        if (cancelled) return
        setStage("amount")
        await sleep(350)
        await typeText("12.990", setAmount)
        if (cancelled) return
        setStage("click")
        await sleep(500)
        setAdded(true)
        setStage("chart")
        await sleep(3200)
      }
    }

    runDemo()
    return () => {
      cancelled = true
    }
  }, [])

  const cursorPosition = {
    service: { left: "33%", top: "32%" },
    amount: { left: "10%", top: "48%" },
    click: { left: "33%", top: "84%" },
    chart: { left: "82%", top: "32%" },
  }[stage]

  return (
    <div className="relative mx-auto max-w-5xl">
      <div className="relative grid gap-6 sm:grid-cols-[0.92fr_1.08fr]">
        <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
          <div className="mb-5 flex items-center justify-between">
            <div><h3 className="text-lg font-semibold text-texto">Gestor de suscripciones</h3></div>
            <span className="text-sm text-texto-dim">Demo</span>
          </div>
          <div className="space-y-3 text-left">
            <div><p className="mb-1 block text-sm text-texto">Nombre del servicio</p><div className="h-10 rounded-xl bg-fondo px-3 py-2 text-sm text-texto">{service}<span className={stage === "service" ? "ml-0.5 inline-block h-4 w-px animate-pulse bg-primario align-middle" : "hidden"} /></div></div>
            <div className="grid gap-4 sm:grid-cols-2"><div><p className="mb-1 block text-sm text-texto">Monto</p><div className="h-10 rounded-xl bg-fondo px-3 py-2 text-sm text-texto">{amount}<span className={stage === "amount" ? "ml-0.5 inline-block h-4 w-px animate-pulse bg-primario align-middle" : "hidden"} /></div></div><div><p className="mb-1 block text-sm text-texto">Divisa</p><div className="flex h-10 items-center rounded-xl bg-fondo px-3 text-sm text-texto">CLP</div></div></div>
            <div><p className="mb-1 block text-sm text-texto">Frecuencia de cobro</p><div className="flex h-10 items-center rounded-xl bg-fondo px-3 text-sm text-texto">Mensual</div></div>
            <div className={`mt-2 flex h-10 items-center justify-center rounded-xl bg-primario/70 px-4 py-2 font-semibold text-slate-950 transition-transform duration-150 ${stage === "click" ? "scale-95" : "scale-100"}`}>Agregar suscripción</div>
          </div>
        </div>

        <div className="rounded-2xl bg-secundario/20 p-5 shadow-lg">
          <div className="mb-6 flex items-start justify-between gap-4"><div><h3 className="text-lg font-semibold text-texto">Gastos por suscripción</h3><p className="mt-1 text-sm text-texto-dim">Distribución de tus suscripciones activas por servicio</p></div><div className="shrink-0 text-right"><p className="text-2xl font-bold text-primario">$ {added ? "46.990" : "32.400"}</p><p className="text-xs text-texto-dim">total registrado</p></div></div>
          <div className="flex h-6 overflow-hidden rounded-full bg-fondo/80 ring-1 ring-white/5" role="img" aria-label="Distribución animada de gastos por suscripción">
            <div className="h-full rounded-l-full bg-sky-400 transition-all duration-1000" style={{ width: added ? "42%" : "58%" }} />
            <div className="h-full bg-amber-400 transition-all duration-1000" style={{ width: added ? "27%" : "42%" }} />
            <div className="h-full rounded-r-full bg-primario transition-all duration-1000" style={{ width: added ? "31%" : "0%" }} />
          </div>
          <div className="mt-5 grid gap-x-5 gap-y-3 sm:grid-cols-2">
            {[{ name: "Spotify", value: added ? "$ 19.740" : "$ 18.792", color: "bg-sky-400", percentage: added ? "42%" : "58%" }, { name: "Adobe", value: added ? "$ 12.660" : "$ 13.608", color: "bg-amber-400", percentage: added ? "27%" : "42%" }, { name: "Netflix", value: "$ 14.590", color: "bg-primario", percentage: "31%" }].map((subscription) => (
              <div key={subscription.name} className={`flex min-w-0 items-center justify-between gap-3 text-sm transition-all duration-700 ${subscription.name === "Netflix" && !added ? "translate-y-2 opacity-0" : "translate-y-0 opacity-100"}`}>
                <div className="flex min-w-0 items-center gap-2"><span className={`h-2.5 w-2.5 shrink-0 rounded-full ${subscription.color}`} /><span className="truncate text-texto">{subscription.name}</span></div>
                <div className="flex shrink-0 items-center gap-2 text-right"><span className="font-semibold text-texto">{subscription.value}</span><span className="w-9 text-xs text-texto-dim">{subscription.percentage}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pointer-events-none absolute z-10 transition-all duration-500 ease-out" style={{ left: cursorPosition.left, top: cursorPosition.top }} aria-hidden="true">
          <svg className="h-8 w-8" viewBox="0 0 24 24" fill="white" stroke="#171923" strokeWidth="1.5">
            <path d="M13.9 19.85c-.05 0-.1 0-.2-.05s-.2-.15-.3-.25l-1.85-4.3-2.25 2.1q-.075.15-.3.15c-.05 0-.15 0-.2-.05-.15-.05-.3-.25-.3-.45V6c0-.2.1-.4.3-.45.05-.05.15-.05.2-.05a.53.53 0 0 1 .35.15l8 7.5c.15.15.2.35.15.55s-.25.3-.45.35l-3.15.3 1.95 4.25c.05.1.05.25 0 .4-.05.1-.15.25-.25.3l-1.45.65c-.1-.1-.2-.1-.25-.1" />
          </svg>
        </div>
      </div>
    </div>
  )
}

export default DemoAnimation;