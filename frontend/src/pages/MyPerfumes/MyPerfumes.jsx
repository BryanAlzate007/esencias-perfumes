import { useEffect, useState } from "react";
import { Alert, Col, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import PerfumeCard from "../../components/PerfumeCard/PerfumeCard";
import { listMyPerfumes } from "../../services/orders";

export default function MyPerfumes() {
  const { t } = useTranslation();
  const [perfumes, setPerfumes] = useState([]);

  useEffect(() => {
    listMyPerfumes().then(setPerfumes).catch(() => setPerfumes([]));
  }, []);

  return (
    <>
      <h1 className="h2 mb-4">{t("myPerfumes.title")}</h1>
      {perfumes.length === 0 && <Alert variant="light">{t("myPerfumes.empty")}</Alert>}
      <Row xs={2} md={3} xl={4} className="g-3">
        {perfumes.map((perfume, index) => (
          <Col key={perfume.id}>
            <PerfumeCard perfume={perfume} index={index} showCart={false} />
          </Col>
        ))}
      </Row>
    </>
  );
}
