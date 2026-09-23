import { useState } from "react";
import { Alert, Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { updateMe } from "../../services/auth";
import "./AdminSettings.css";

export default function AdminSettings() {
  const { t } = useTranslation();
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    country: user?.country || "",
  });
  const [saved, setSaved] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const updated = await updateMe(form);
    setUser(updated);
    setSaved(true);
  }

  return (
    <>
      <h1 className="h2 mb-3">{t("admin.settingsTitle")}</h1>
      <p className="text-body-secondary">{t("admin.settingsHelp")}</p>
      {saved && <Alert variant="success">{t("profile.saved")}</Alert>}
      <Form className="mt-4" style={{ maxWidth: "28rem" }} onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>{t("auth.name")}</Form.Label>
          <Form.Control
            value={form.first_name}
            onChange={(event) => setForm((current) => ({ ...current, first_name: event.target.value }))}
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>{t("auth.country")}</Form.Label>
          <Form.Control
            value={form.country}
            onChange={(event) => setForm((current) => ({ ...current, country: event.target.value }))}
          />
        </Form.Group>
        <Button type="submit" variant="dark">
          {t("admin.save")}
        </Button>
      </Form>
      <section className="perfume-settings-card">
        <h2>{t("admin.perfumeSettings")}</h2>
        <Link className="perfume-settings-link" to="/admin/configuraciones/acordes">
          {t("admin.mainChords")}
        </Link>
        <Link className="perfume-settings-link" to="/admin/configuraciones/envases">
          {t("admin.containers")}
        </Link>
        <Link className="perfume-settings-link" to="/admin/configuraciones/perfiles">
          {t("admin.personalProfile")}
        </Link>
      </section>
    </>
  );
}
