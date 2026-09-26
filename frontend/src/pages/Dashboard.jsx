import { useSubscriptions } from "../hooks/useSubscriptions";
import { useAuth } from "../utils/useAuth";
import Navbar from "../components/Navbar";
import CifraCard from "../components/dashboard/CifraCard";
import GraphCard from "../components/dashboard/GraphCard";
import ProximosCobros from "../components/dashboard/ProximosCobros";
import FormularioSuscripcion from "../components/dashboard/FormularioSuscripcion";
import ListaSuscripcion from "../components/dashboard/ListaSuscripcion";


function Dashboard() {
  const { user } = useAuth();
  const {
    totalMonthlySpend,
    pendienteEsteMes,
    activeSubscriptions,
    upcomingCharges,
    totalVentana,
    ventanaParcial,
    diasAlerta,
    subscriptions,
    form,
    handleChange,
    handleSubmit,
    resetForm,
    handleEdit,
    toggleSubscription,
    renovarCobro,
    isLoading,
    error,
  } = useSubscriptions();

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
              {user?.nombre && (
                <p className="mt-1 text-sm text-texto-dim">Hola, {user.nombre}</p>
              )}
            </div>
          </header>

          {error && (
            <div className="mb-6 rounded-xl bg-red-500/15 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          {isLoading && (
            <p className="mb-6 text-sm text-texto-dim">Cargando tus suscripciones...</p>
          )}

          <section className="grid gap-4 md:grid-cols-2">
            {/* El total viene de /api/suscripciones/resumen, no se recalcula acá:
                es la misma cifra que entrega la API, con las anuales prorrateadas. */}
            <CifraCard texto="Gasto mensual" numero={totalMonthlySpend} />
            <CifraCard texto="Pendiente este mes" numero={pendienteEsteMes} />
          </section>

          <section className="mt-8 grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
            <GraphCard subscriptions={activeSubscriptions}/>
            <ProximosCobros
              upcomingCharges={upcomingCharges}
              totalVentana={totalVentana}
              ventanaParcial={ventanaParcial}
              diasAlerta={diasAlerta}
              renovarCobro={renovarCobro}
            />
          </section>

          <section className="mt-8 grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
            <FormularioSuscripcion
              form={form}
              handleChange={handleChange}
              handleSubmit={handleSubmit}
              resetForm={resetForm}
            />
            <ListaSuscripcion
              subscriptions={subscriptions}
              handleEdit={handleEdit}
              toggleSubscription={toggleSubscription}
            />
          </section>
        </div>
      </div>
    </>
  );
}

export default Dashboard;