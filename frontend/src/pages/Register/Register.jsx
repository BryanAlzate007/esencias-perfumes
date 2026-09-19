import { useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { allauthErrors, signUp } from "../../lib/allauth";
import { useAuth } from "../../hooks/useAuth";

export default function Register() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    first_name: "",
    email: "",
    password: "",
    country: "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const result = await signUp(form);
    if (!(result.status === 200 && result.meta?.is_authenticated)) {
      setError(allauthErrors(result) || t("common.error"));
      setSaving(false);
      return;
    }
    await refreshUser();
    navigate("/", { replace: true });
  }

  return (
    <Card className="auth-card shadow-sm mx-auto">
      <Card.Body className="p-4">
        <h1 className="h3 mb-4">{t("auth.registerTitle")}</h1>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.username")}</Form.Label>
            <Form.Control name="username" value={form.username} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.name")}</Form.Label>
            <Form.Control name="first_name" value={form.first_name} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.email")}</Form.Label>
            <Form.Control type="email" name="email" value={form.email} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.country")}</Form.Label>
            <Form.Control name="country" value={form.country} onChange={update} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.password")}</Form.Label>
            <Form.Control type="password" name="password" value={form.password} onChange={update} required />
          </Form.Group>
          <Button type="submit" variant="dark" className="w-100" disabled={saving}>
            {t("auth.submitRegister")}
          </Button>
        </Form>
        <div className="mt-3 small">
          <Link to="/login">{t("auth.hasAccount")}</Link>
        </div>
      </Card.Body>
    </Card>
  );
}
