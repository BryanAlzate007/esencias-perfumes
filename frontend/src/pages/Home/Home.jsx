import { useEffect, useState } from "react";
import { Alert, Col, Row, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Navigate } from "react-router-dom";
import PerfumeCard from "../../components/PerfumeCard/PerfumeCard";
import { useAuth } from "../../hooks/useAuth";
import { useCart } from "../../hooks/useCart";
import { listPerfumes } from "../../services/perfumes";

export default function Home() {
  const { t } = useTranslation();
  const { isAdmin, isAuthenticated } = useAuth();
  const { addItem } = useCart();
  const [perfumes, setPerfumes] = useState([]);
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    listPerfumes()
      .then((data) => {
        setPerfumes(data.results || []);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  if (isAdmin) {
    return <Navigate to="/admin/catalogo" replace />;
  }

  async function handleAdd(id) {
    if (!isAuthenticated) {
      setMessage(t("cart.loginRequired"));
      return;
    }
    await addItem(id);
    setMessage(t("home.added"));
  }

  return (
    <>
      <div className="mb-4">
        <p className="text-body-secondary mb-1">{t("app.tagline")}</p>
        <h1 className="h2 mb-2">{t("home.title")}</h1>
        <p className="mb-0">{t("home.subtitle")}</p>
      </div>
      {message && <Alert variant="info">{message}</Alert>}
      {status === "loading" && (
        <div className="d-flex align-items-center gap-2">
          <Spinner animation="border" size="sm" />
          <span>{t("common.loading")}</span>
        </div>
      )}
      {status === "error" && <Alert variant="warning">{t("common.error")}</Alert>}
      {status === "ready" && perfumes.length === 0 && <Alert variant="light">{t("home.empty")}</Alert>}
      <Row xs={1} md={2} xl={3} className="g-4">
        {perfumes.map((perfume) => (
          <Col key={perfume.id}>
            <PerfumeCard perfume={perfume} canShop={isAuthenticated} onAddToCart={handleAdd} />
          </Col>
        ))}
      </Row>
    </>
  );
}
