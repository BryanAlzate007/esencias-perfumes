import { useEffect } from "react";
import { Alert, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function AuthCallback() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const error = params.get("error");

  useEffect(() => {
    if (error) {
      return;
    }
    let cancelled = false;
    refreshUser()
      .then((me) => {
        if (cancelled) {
          return;
        }
        const next = sessionStorage.getItem("esencias-auth-next") || "/";
        sessionStorage.removeItem("esencias-auth-next");
        navigate(me?.is_admin ? "/admin/catalogo" : next, { replace: true });
      })
      .catch(() => {
        if (!cancelled) {
          navigate("/", { replace: true });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [error, navigate, refreshUser]);

  if (error) {
    return <Alert variant="danger">{t("auth.socialError")}</Alert>;
  }

  return (
    <div className="d-flex justify-content-center py-5">
      <Spinner animation="border" />
    </div>
  );
}
