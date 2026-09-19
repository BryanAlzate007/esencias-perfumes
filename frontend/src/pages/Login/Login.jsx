import { useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { allauthErrors, login } from "../../lib/allauth";
import { useAuth } from "../../hooks/useAuth";

export default function Login() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const identifier = form.username.includes("@")
      ? { email: form.username, password: form.password }
      : { username: form.username, password: form.password };
    const result = await login(identifier);
    if (result.status !== 200 || !result.meta?.is_authenticated) {
      setError(allauthErrors(result) || t("common.error"));
      setSaving(false);
      return;
    }
    const me = await refreshUser();
    const next = location.state?.from || (me?.is_admin ? "/admin/catalogo" : "/");
    navigate(me?.is_admin ? "/admin/catalogo" : next, { replace: true });
  }

  return (
    <Card className="auth-card shadow-sm mx-auto">
      <Card.Body className="p-4">
        <h1 className="h3 mb-4">{t("auth.loginTitle")}</h1>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.username")}</Form.Label>
            <Form.Control name="username" value={form.username} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.password")}</Form.Label>
            <Form.Control type="password" name="password" value={form.password} onChange={update} required />
          </Form.Group>
          <Button type="submit" variant="dark" className="w-100" disabled={saving}>
            {t("auth.submitLogin")}
          </Button>
        </Form>
        <div className="mt-3 d-flex justify-content-between small">
          <Link to="/recuperar-contrasena">{t("auth.forgotLink")}</Link>
          <Link to="/registro">{t("auth.noAccount")}</Link>
        </div>
      </Card.Body>
    </Card>
  );
}
