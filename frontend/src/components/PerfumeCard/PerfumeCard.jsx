import { Button, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

function formatDate(value, language) {
  if (!value) {
    return null;
  }
  return new Intl.DateTimeFormat(language, { dateStyle: "medium" }).format(new Date(value));
}

export default function PerfumeCard({ perfume, onAddToCart, canShop }) {
  const { t, i18n } = useTranslation();
  const lastReview = formatDate(perfume.last_review_at, i18n.language) || t("home.noReviews");

  return (
    <Card className="h-100 perfume-card shadow-sm">
      <Link to={`/perfumes/${perfume.id}`} className="text-decoration-none text-body">
        <Card.Img
          variant="top"
          src={perfume.image_url}
          alt={perfume.name}
          className="perfume-card-image"
        />
        <Card.Body>
          <Card.Subtitle className="text-body-secondary mb-1">{perfume.brand}</Card.Subtitle>
          <Card.Title as="h2" className="h5">
            {perfume.name}
          </Card.Title>
          <Card.Text className="perfume-card-text">{perfume.description}</Card.Text>
          <p className="small text-body-secondary mb-0">
            {t("home.lastReview")}: {lastReview}
          </p>
        </Card.Body>
      </Link>
      <Card.Footer className="bg-transparent d-flex justify-content-between align-items-center">
        <strong>${Number(perfume.price).toFixed(2)}</strong>
        {canShop && (
          <Button size="sm" variant="dark" onClick={() => onAddToCart(perfume.id)}>
            {t("home.addToCart")}
          </Button>
        )}
      </Card.Footer>
    </Card>
  );
}
