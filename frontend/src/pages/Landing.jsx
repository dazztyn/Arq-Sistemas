import Navbar from "../components/Navbar"
import { Link } from "react-router-dom"
import DemoAnimation from "../utils/DemoAnimation"

function Landing() {
	return (
  	<div className="min-h-screen overflow-hidden bg-fondo text-texto [background-image:radial-gradient(circle_at_78%_20%,rgba(51,42,120,0.72),transparent_28rem),radial-gradient(circle_at_8%_78%,rgba(141,255,75,0.06),transparent_24rem),linear-gradient(115deg,#282b39_0%,#282b39_55%,#242631_100%)]">
      <Navbar />
      <main>
          <section className="relative isolate">
            <div className="absolute inset-0 -z-10 [background-image:linear-gradient(rgba(208,207,216,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(208,207,216,0.045)_1px,transparent_1px)] [background-size:4rem_4rem] [mask-image:linear-gradient(to_bottom,black,transparent_82%)]" aria-hidden="true" />
          <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 pb-20 pt-16 lg:grid-cols-[0.9fr_1.1fr] lg:px-8 lg:pb-28 lg:pt-24">
              <div>
              <p className="mb-6 flex items-center gap-3 text-sm font-bold uppercase tracking-[0.22em] text-primario">
                <span className="h-px w-8 bg-primario" />
                Finanzas personales, sin ruido
              </p>
              <h1 className="max-w-2xl text-5xl font-black leading-[0.98] tracking-tight text-texto sm:text-6xl lg:text-7xl">
                Tus suscripciones, <span className="text-primario">bajo control.</span>
              </h1>
              <p className="mt-7 max-w-xl text-lg leading-8 text-texto-dim sm:text-xl">
                Una vista clara de todo lo que pagas cada mes. Detecta fugas, anticipa cobros y recupera espacio en tu presupuesto.
              </p>
              <div className="mt-9 flex flex-col gap-4 sm:flex-row sm:items-center">
                <Link to="/register" className="inline-flex items-center justify-center gap-3 rounded-full bg-primario px-6 py-3.5 text-base font-bold text-fondo transition hover:-translate-y-1 hover:bg-acento hover:shadow-lg hover:shadow-acento/20">
                  Empezar gratis <span aria-hidden="true">-&gt;</span>
                </Link>
                <a href="#como-funciona" className="inline-flex items-center justify-center px-3 py-3 text-base font-bold text-texto transition hover:text-primario">
                  Ver cómo funciona <span className="ml-2 text-primario" aria-hidden="true">↓</span>
                </a>
              </div>
            </div>
          </div>
        </section>

        <section id="como-funciona">
          <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-28">
            <div className="mx-auto mb-12 max-w-2xl text-center"><p className="mb-4 text-sm font-bold uppercase tracking-[0.22em] text-primario">Así de simple</p><h2 className="text-3xl font-black text-texto sm:text-5xl">De un gasto suelto a una decisión clara.</h2><p className="mt-5 text-lg leading-8 text-texto-dim">Mira cómo una nueva suscripción se suma a tu panorama financiero en segundos.</p></div>
            <DemoAnimation />
          </div>
        </section>
        
        <footer className="border-y border-secundario/70 bg-secundario/45">
          <div className="mx-auto grid max-w-7xl gap-8 px-6 py-12 sm:grid-cols-3 lg:px-8 lg:py-16">
            {[["01", "Registra", "Añade tus servicios en segundos."], ["02", "Observa", "Entiende a dónde va tu dinero."], ["03", "Decide", "Cancela lo que ya no necesitas."]].map(([number, title, description]) => (
              <div key={number} className="flex gap-4"><span className="text-sm font-black text-primario">{number}</span><div><h2 className="font-bold text-texto">{title}</h2><p className="mt-1 text-sm leading-6 text-texto-dim">{description}</p></div></div>
            ))}
          </div>
        </footer>
      </main>
    </div>
  )
}

export default Landing