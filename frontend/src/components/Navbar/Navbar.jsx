import { Badge, Button, Container, Nav, Navbar } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useCart } from "../../hooks/useCart";

export default function AppNavbar() {
  const { t } = useTranslation();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { count, setOpen } = useCart();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  const customerLinks = [
    { to: "/", label: t("nav.home") },
    { to: "/tus-perfumes", label: t("nav.yourPerfumes") },
    { to: "/pedidos", label: t("nav.orders") },
    { to: "/comentarios", label: t("nav.comments") },
  ];

  const adminLinks = [
    { to: "/admin/catalogo", label: t("nav.catalog") },
    { to: "/admin/pedidos", label: t("nav.orders") },
    { to: "/admin/usuarios", label: t("nav.users") },
    { to: "/admin/comentarios", label: t("nav.comments") },
    { to: "/admin/configuraciones", label: t("nav.settings") },
  ];

  const guestLinks = [{ to: "/", label: t("nav.home") }];
  const links = isAdmin ? adminLinks : isAuthenticated ? customerLinks : guestLinks;

  return (
    <Navbar expand="lg" className="border-bottom bg-body" sticky="top">
      <Container>
        <Navbar.Brand as={NavLink} to={isAdmin ? "/admin/catalogo" : "/"}>
          {t("app.name")}
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="main-navigation" />
        <Navbar.Collapse id="main-navigation">
          <Nav className="me-auto">
            {links.map((link) => (
              <Nav.Link as={NavLink} to={link.to} end={link.to === "/"} key={link.to}>
                {link.label}
              </Nav.Link>
            ))}
          </Nav>
          <Nav className="align-items-lg-center gap-lg-2">
            {isAuthenticated && !isAdmin && (
              <Button variant="outline-secondary" size="sm" onClick={() => setOpen(true)}>
                {t("nav.cart")} {count > 0 && <Badge bg="dark">{count}</Badge>}
              </Button>
            )}
            {!isAuthenticated && (
              <>
                <Nav.Link as={NavLink} to="/login">
                  {t("nav.login")}
                </Nav.Link>
                <Nav.Link as={NavLink} to="/registro">
                  {t("nav.register")}
                </Nav.Link>
              </>
            )}
            {isAuthenticated && (
              <>
                <Navbar.Text className="px-lg-2">{user.first_name || user.username}</Navbar.Text>
                <Button variant="outline-secondary" size="sm" onClick={handleLogout}>
                  {t("nav.logout")}
                </Button>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
