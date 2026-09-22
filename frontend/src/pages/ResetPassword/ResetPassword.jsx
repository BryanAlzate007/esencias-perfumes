import { useEffect, useState } from "react";
import { Alert, Button, Card, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router-dom";
import { allauthErrors, getPasswordReset, resetPassword } from "../../lib/allauth";
import { useAuthModal } from "../../hooks/useAuthModal";

export default function ResetPassword() {
  const { t } = useTranslation();
  const { key } = useParams();
  const navigate = useNavigate();
  const { openLogin } = useAuthModal();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [valid, setValid] = useState(false);

  useEffect(() => {
    getPasswordReset(key).then((result) => {
      if (result.status === 200) {
        setValid(true);
      } else {
        setError(allauthErrors(result) || t("common.error"));
      }
    });
  }, [key, t]);

  async function handleSubmit(event) {
    event.preventDefault();
    const result = await resetPassword({ key, password });
    if (result.status !== 200) {
      setError(allauthErrors(result) || t("common.error"));
      return;
    }
    navigate("/", { replace: true });
    openLogin("/");
  }

  return (
    <Card className="auth-card shadow-sm mx-auto">
      <Card.Body className="p-4">
        <h1 className="h3 mb-4">{t("auth.resetTitle")}</h1>
        {error && <Alert variant="danger">{error}</Alert>}
        {valid && (
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>{t("auth.password")}</Form.Label>
              <Form.Control type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            </Form.Group>
            <Button type="submit" variant="dark" className="w-100">
              {t("auth.submitReset")}
            </Button>
          </Form>
        )}
      </Card.Body>
    </Card>
  );
}
