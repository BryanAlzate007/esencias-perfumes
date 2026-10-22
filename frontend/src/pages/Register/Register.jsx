import { useEffect, useRef, useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { allauthErrors, signUp } from "../../lib/allauth";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import { useTheme } from "../../hooks/useTheme";
import Recaptcha from "../../components/Recaptcha/Recaptcha";
import SocialAuthButtons from "../../components/SocialAuthButtons/SocialAuthButtons";
import { getCaptchaConfig } from "../../services/auth";
import { claimReferral } from "../../services/referrals";
import "../../components/LoginModal/LoginModal.css";

export default function Register() {
  const { t, i18n } = useTranslation();
  const { refreshUser } = useAuth();
  const { openLogin } = useAuthModal();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const captchaRef = useRef(null);
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
  const [siteKey, setSiteKey] = useState("");
  const [captchaAction, setCaptchaAction] = useState("SIGNUP");
  const [captchaToken, setCaptchaToken] = useState("");
  const [captchaFailed, setCaptchaFailed] = useState(false);

  useEffect(() => {
    const code = params.get("ref");
    if (code) {
      sessionStorage.setItem("esencias-referral", code);
    }
  }, [params]);

  useEffect(() => {
    let cancelled = false;
    getCaptchaConfig()
      .then((config) => {
        if (!cancelled) {
          setSiteKey(config.site_key || "");
          setCaptchaAction(config.action || "SIGNUP");
          setCaptchaFailed(!config.site_key);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCaptchaFailed(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!captchaToken) {
      setError(t("auth.captchaRequired"));
      return;
    }
    setSaving(true);
    setError("");
    const result = await signUp({ ...form, captcha: captchaToken });
    if (!(result.status === 200 && result.meta?.is_authenticated)) {
      captchaRef.current?.reset();
      setError(allauthErrors(result) || t("common.error"));
      setSaving(false);
      return;
    }
    await refreshUser();
    const code = sessionStorage.getItem("esencias-referral");
    if (code) {
      try {
        await claimReferral(code);
      } catch {
        // The account is already created; an invalid code should not block signup.
      }
      sessionStorage.removeItem("esencias-referral");
    }
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
          {captchaFailed ? (
            <Alert variant="warning">{t("auth.captchaError")}</Alert>
          ) : (
            <Recaptcha
              ref={captchaRef}
              siteKey={siteKey}
              action={captchaAction}
              theme={theme}
              language={i18n.language}
              onChange={setCaptchaToken}
              onError={() => setCaptchaFailed(true)}
            />
          )}
          <Button type="submit" variant="dark" className="w-100" disabled={saving || !captchaToken}>
            {t("auth.submitRegister")}
          </Button>
        </Form>
        <div className="mt-3 small">
          <button type="button" className="btn btn-link p-0" onClick={() => openLogin("/registro")}>
            {t("auth.hasAccount")}
          </button>
        </div>
        <p className="mt-3 mb-0 text-center small">
          <Link to="/politica-de-privacidad">{t("nav.privacy")}</Link>
        </p>
      </Card.Body>
    </Card>
  );
}
