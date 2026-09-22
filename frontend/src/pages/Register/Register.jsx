import { useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { allauthErrors, signUp } from "../../lib/allauth";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import SocialAuthButtons from "../../components/SocialAuthButtons/SocialAuthButtons";
import "../../components/LoginModal/LoginModal.css";

export default function Register() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const { openLogin } = useAuthModal();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    phone: "",
    country: "",
    whatsapp: "",
    password: "",
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
        <SocialAuthButtons process="login" />
        <p className="social-auth-divider">{t("auth.orEmail")}</p>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.username")}</Form.Label>
            <Form.Control name="username" value={form.username} onChange={update} required autoComplete="username" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.email")}</Form.Label>
            <Form.Control type="email" name="email" value={form.email} onChange={update} required autoComplete="email" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.phone")}</Form.Label>
            <Form.Control name="phone" value={form.phone} onChange={update} required autoComplete="tel" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.country")}</Form.Label>
            <Form.Control name="country" value={form.country} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.whatsapp")}</Form.Label>
            <Form.Control name="whatsapp" value={form.whatsapp} onChange={update} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.password")}</Form.Label>
            <Form.Control
              type="password"
              name="password"
              value={form.password}
              onChange={update}
              required
              autoComplete="new-password"
            />
          </Form.Group>
          <Button type="submit" variant="dark" className="w-100" disabled={saving}>
            {t("auth.submitRegister")}
          </Button>
        </Form>
        <div className="mt-3 small">
          <button type="button" className="btn btn-link p-0" onClick={() => openLogin("/registro")}>
            {t("auth.hasAccount")}
          </button>
        </div>
      </Card.Body>
    </Card>
  );
}
