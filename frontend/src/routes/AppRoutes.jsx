import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../components/ProtectedRoute";
import MainLayout from "../layouts/MainLayout";
import AdminCatalog from "../pages/admin/AdminCatalog";
import AdminLookup from "../pages/admin/AdminLookup";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminSettings from "../pages/admin/AdminSettings";
import AdminUsers from "../pages/admin/AdminUsers";
import Comments from "../pages/Comments/Comments";
import ForgotPassword from "../pages/ForgotPassword/ForgotPassword";
import Home from "../pages/Home/Home";
import Login from "../pages/Login/Login";
import AuthCallback from "../pages/AuthCallback/AuthCallback";
import MyPerfumes from "../pages/MyPerfumes/MyPerfumes";
import Orders from "../pages/Orders/Orders";
import PerfumeDetail from "../pages/PerfumeDetail/PerfumeDetail";
import Register from "../pages/Register/Register";
import ResetPassword from "../pages/ResetPassword/ResetPassword";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/perfumes/:id" element={<PerfumeDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Register />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/recuperar-contrasena" element={<ForgotPassword />} />
        <Route path="/recuperar-contrasena/key/:key" element={<ResetPassword />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/tus-perfumes" element={<MyPerfumes />} />
          <Route path="/pedidos" element={<Orders />} />
          <Route path="/comentarios" element={<Comments />} />
        </Route>

        <Route element={<ProtectedRoute adminOnly />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/catalogo" element={<AdminCatalog />} />
          <Route path="/admin/pedidos" element={<Orders />} />
          <Route path="/admin/usuarios" element={<AdminUsers />} />
          <Route path="/admin/comentarios" element={<Comments />} />
          <Route path="/admin/configuraciones" element={<AdminSettings />} />
          <Route path="/admin/configuraciones/:section" element={<AdminLookup />} />
        </Route>
      </Route>
    </Routes>
  );
}
