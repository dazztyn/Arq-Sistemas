import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "./utils/ProtectedRoute";
import Login from "./pages/Login"
import Landing from "./pages/Landing"
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/dashboard"
        element={
            <ProtectedRoute allowedRoles={["admin", "usuario"]}>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<NotFound />} />
      
    </Routes>
  )
}

export default App
