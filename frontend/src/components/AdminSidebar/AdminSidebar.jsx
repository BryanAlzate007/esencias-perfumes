import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";
import "./AdminSidebar.css";

export default function AdminSidebar({ open, docked, onClose }) {
  const { t } = useTranslation();
  const links = [
    { to: "/admin", label: t("nav.dashboard"), end: true },
    { to: "/admin/catalogo", label: t("nav.catalog") },
    { to: "/admin/pedidos", label: t("nav.orders") },
    { to: "/admin/usuarios", label: t("nav.users") },
    { to: "/admin/comentarios", label: t("nav.comments") },
    { to: "/admin/configuraciones", label: t("nav.settings") },
  ];

  useEffect(() => {
    if (!open || docked) {
      return undefined;
    }
    function onKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, docked, onClose]);

  function handleNavigate() {
    if (!docked) {
      onClose();
    }
  }

  return (
    <>
      {open && !docked && <button type="button" className="admin-sidebar-backdrop" aria-label={t("nav.closeAdminMenu")} onClick={onClose} />}
      <aside className={`admin-sidebar${open ? " is-open" : ""}`} aria-hidden={!open}>
        <p className="admin-sidebar-kicker">{t("nav.adminMenu")}</p>
        <nav className="admin-sidebar-nav" aria-label={t("nav.adminMenu")}>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className="admin-sidebar-link"
              tabIndex={open ? 0 : -1}
              onClick={handleNavigate}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
