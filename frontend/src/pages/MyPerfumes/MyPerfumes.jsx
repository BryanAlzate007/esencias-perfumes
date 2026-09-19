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
      <Row xs={1} md={2} xl={3} className="g-4">
        {perfumes.map((perfume) => (
          <Col key={perfume.id}>
            <PerfumeCard perfume={perfume} />
          </Col>
        ))}
      </Row>
    </>
  );
}
