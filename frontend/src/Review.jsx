import GraphCard from "./components/GraphCard"
import { initialSubscriptions } from "./services/Subscripciones.service"

function Review() {
  return (
    <div className="bg-fondo min-h-screen flex items-center justify-center">
      <GraphCard subscriptions={initialSubscriptions} />
    </div>
  )
}

export default Review