import { useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { allauthErrors, requestPasswordReset } from "../../lib/allauth";

export default function ForgotPassword() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    const result = await requestPasswordReset(email);
    if (result.status !== 200) {
      setError(allauthErrors(result) || t("common.error"));
      return;
    }
    setSent(true);
  }

  return (
    <Card className="auth-card shadow-sm mx-auto">
      <Card.Body className="p-4">
        <h1 className="h3 mb-4">{t("auth.forgotTitle")}</h1>
        {error && <Alert variant="danger">{error}</Alert>}
        {sent ? (
          <Alert variant="success">{t("auth.forgotSent")}</Alert>
        ) : (
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>{t("auth.email")}</Form.Label>
              <Form.Control type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </Form.Group>
            <Button type="submit" variant="dark" className="w-100">
              {t("auth.submitForgot")}
            </Button>
          </Form>
        )}
      </Card.Body>
    </Card>
  );
}
