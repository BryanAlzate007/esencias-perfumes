import { useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { allauthErrors, login } from "../../lib/allauth";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import SocialAuthButtons from "../SocialAuthButtons/SocialAuthButtons";
import "./LoginModal.css";

export default function LoginModal() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const { open, closeLogin, redirectTo } = useAuthModal();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  function handleClose() {
    setError("");
    setSaving(false);
    closeLogin();
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
    handleClose();
    const next = redirectTo || "/";
    navigate(me?.is_admin ? "/admin/catalogo" : next, { replace: true });
  }

  return (
    <Modal show={open} onHide={handleClose} centered className="login-modal">
      <Modal.Header closeButton>
        <Modal.Title>{t("auth.loginTitle")}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        <SocialAuthButtons process="login" />
        <p className="social-auth-divider">{t("auth.orEmail")}</p>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.username")}</Form.Label>
            <Form.Control name="username" value={form.username} onChange={update} required autoComplete="username" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>{t("auth.password")}</Form.Label>
            <Form.Control
              type="password"
              name="password"
              value={form.password}
              onChange={update}
              required
              autoComplete="current-password"
            />
          </Form.Group>
          <Button type="submit" variant="dark" className="w-100" disabled={saving}>
            {t("auth.submitLogin")}
          </Button>
        </Form>
        <div className="mt-3 d-flex justify-content-between small">
          <Link to="/recuperar-contrasena" onClick={handleClose}>
            {t("auth.forgotLink")}
          </Link>
          <Link to="/registro" onClick={handleClose}>
            {t("auth.noAccount")}
          </Link>
        </div>
      </Modal.Body>
    </Modal>
  );
}
