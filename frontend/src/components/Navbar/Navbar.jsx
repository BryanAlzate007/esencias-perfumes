import { Badge, Button, Container, Nav, Navbar, NavDropdown } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import { useCart } from "../../hooks/useCart";
import { useTheme } from "../../hooks/useTheme";
import "./Navbar.css";

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path strokeLinecap="round" d="M12 3v1.6M12 19.4V21M4.93 4.93l1.13 1.13M17.94 17.94l1.13 1.13M3 12h1.6M19.4 12H21M4.93 19.07l1.13-1.13M17.94 6.06l1.13-1.13" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.4 14.2A8.2 8.2 0 0 1 9.8 3.6 8.4 8.4 0 1 0 20.4 14.2Z" />
    </svg>
  );
}

function AppearanceControls({ language, theme, t, onLanguage, onTheme, menuId }) {
  const isDark = theme === "dark";

  return (
    <>
      <NavDropdown id={menuId} title={language === "en" ? "EN" : "ES"} align="end">
        <NavDropdown.Item active={language === "es"} onClick={() => onLanguage("es")}>
          Español
        </NavDropdown.Item>
        <NavDropdown.Item active={language === "en"} onClick={() => onLanguage("en")}>
          English
        </NavDropdown.Item>
      </NavDropdown>
      <button
        type="button"
        className="theme-toggle"
        onClick={onTheme}
        aria-label={isDark ? t("theme.light") : t("theme.dark")}
        title={isDark ? t("theme.light") : t("theme.dark")}
      >
        {isDark ? <SunIcon /> : <MoonIcon />}
      </button>
    </>
  );
}

export default function AppNavbar({ adminNavOpen = false, onToggleAdminNav }) {
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { count, setOpen } = useCart();
  const { theme, toggleTheme } = useTheme();
  const { openLogin } = useAuthModal();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const language = (i18n.resolvedLanguage || i18n.language || "es").startsWith("en") ? "en" : "es";

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  function changeLanguage(next) {
    i18n.changeLanguage(next);
    document.documentElement.lang = next;
  }

  const customerLinks = [
    { to: "/", label: t("nav.home") },
    { to: "/tus-perfumes", label: t("nav.yourPerfumes") },
    { to: "/pedidos", label: t("nav.orders") },
    { to: "/comentarios", label: t("nav.comments") },
  ];

  const guestLinks = [
    { to: "/", label: t("nav.home") },
    { to: "/#coleccion", label: t("home.collectionCta"), hash: "coleccion" },
    { to: "/#historia", label: t("home.storyCta"), hash: "historia" },
    { to: "/#contacto", label: t("home.contactTitle"), hash: "contacto" },
  ];
  const links = isAuthenticated && !isAdmin ? customerLinks : guestLinks;

  const appearance = {
    language,
    theme,
    t,
    onLanguage: changeLanguage,
    onTheme: toggleTheme,
  };

  return (
    <Navbar expand="lg" sticky="top" className={`navbar-esencias border-bottom bg-body${pathname === "/" ? " navbar-home" : ""}${adminNavOpen && pathname === "/" ? " navbar-admin-open" : ""}`}>
      <Container>
        {onToggleAdminNav && (
          <button
            type="button"
            className={`admin-nav-toggle${adminNavOpen ? " is-open" : ""}`}
            onClick={onToggleAdminNav}
            aria-expanded={adminNavOpen}
            aria-label={adminNavOpen ? t("nav.closeAdminMenu") : t("nav.adminMenu")}
          >
            <span />
            <span />
            <span />
          </button>
        )}
        <Navbar.Brand as={NavLink} to="/" className="navbar-esencias-brand">
          {t("app.name")}
        </Navbar.Brand>
        <div className="d-flex d-lg-none align-items-center gap-1 ms-auto me-2">
          <AppearanceControls {...appearance} menuId="language-switcher-mobile" />
        </div>
        <Navbar.Toggle aria-controls="main-navigation" />
        <Navbar.Collapse id="main-navigation">
          <Nav className="mx-lg-auto">
            {links.map((link) => (
              <Nav.Link
                as={NavLink}
                to={link.to}
                end={link.to === "/"}
                key={link.to}
                onClick={(event) => {
                  if (link.hash && pathname === "/") {
                    event.preventDefault();
                    document.getElementById(link.hash)?.scrollIntoView({ behavior: "smooth", block: "start" });
                  }
                }}
              >
                {link.label}
              </Nav.Link>
            ))}
          </Nav>
          <Nav className="align-items-lg-center gap-lg-2">
            <div className="d-none d-lg-flex align-items-center gap-2 me-lg-2">
              <AppearanceControls {...appearance} menuId="language-switcher" />
            </div>
            {isAuthenticated && !isAdmin && (
              <Button variant="outline-secondary" size="sm" onClick={() => setOpen(true)}>
                {t("nav.cart")} {count > 0 && <Badge bg="dark">{count}</Badge>}
              </Button>
            )}
            {!isAuthenticated && (
              <>
                <Button variant="outline-secondary" size="sm" className="navbar-shop-btn" onClick={() => openLogin("/")}>
                  {t("nav.login")}
                </Button>
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
