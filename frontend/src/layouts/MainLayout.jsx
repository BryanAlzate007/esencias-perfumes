import { Outlet } from "react-router-dom";
import { Container } from "react-bootstrap";
import AppNavbar from "../components/Navbar/Navbar";
import CartDrawer from "../components/CartDrawer/CartDrawer";

export default function MainLayout() {
  return (
    <>
      <AppNavbar />
      <Container as="main" className="py-4 py-md-5">
        <Outlet />
      </Container>
      <CartDrawer />
    </>
  );
}
