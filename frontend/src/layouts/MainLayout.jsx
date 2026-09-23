import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Container } from "react-bootstrap";
import AdminSidebar from "../components/AdminSidebar/AdminSidebar";
import AppNavbar from "../components/Navbar/Navbar";
import CartDrawer from "../components/CartDrawer/CartDrawer";
import { useAuth } from "../hooks/useAuth";

function useDesktopNav() {
  const query = "(min-width: 992px)";
  const [isDesktop, setIsDesktop] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const media = window.matchMedia(query);
    const onChange = () => setIsDesktop(media.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return isDesktop;
}

export default function MainLayout() {
  const { pathname } = useLocation();
  const { isAdmin, ready } = useAuth();
  const isDesktop = useDesktopNav();
  const isHome = pathname === "/";
  const isAdminRoute = pathname.startsWith("/admin");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!ready) {
      return;
    }
    setSidebarOpen(isAdmin && isAdminRoute && isDesktop);
  }, [ready, isAdmin, isAdminRoute, isDesktop]);

  const docked = isAdmin && isAdminRoute && isDesktop && sidebarOpen;

  return (
    <div className={docked ? "app-shell-admin-open" : undefined}>
      <AppNavbar
        adminNavOpen={sidebarOpen}
        onToggleAdminNav={isAdmin ? () => setSidebarOpen((open) => !open) : undefined}
      />
      {isAdmin && (
        <AdminSidebar open={sidebarOpen} docked={docked} onClose={() => setSidebarOpen(false)} />
      )}
      <div className="app-main">
        {isHome ? (
          <Outlet />
        ) : (
          <Container as="main" className="py-4 py-md-5">
            <Outlet />
          </Container>
        )}
      </div>
      <CartDrawer />
    </div>
  );
}
