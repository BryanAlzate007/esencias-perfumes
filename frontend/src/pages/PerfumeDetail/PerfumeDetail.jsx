import { useEffect, useState } from "react";
import { Alert, Badge, Button, Col, Form, Image, Row, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useCart } from "../../hooks/useCart";
import { getPerfume } from "../../services/perfumes";
import {
  createPerfumeReview,
  getCommunity,
  listPerfumeReviews,
  setOccasion,
  setRating,
} from "../../services/reviews";

const SENTIMENTS = ["love", "like", "neutral", "dislike", "hate"];
const OCCASIONS = ["winter", "spring", "summer", "autumn", "day", "night"];

function formatDate(value, language) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat(language, { dateStyle: "medium" }).format(new Date(value));
}

export default function PerfumeDetail() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { isAuthenticated } = useAuth();
  const { addItem } = useCart();
  const [perfume, setPerfume] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [community, setCommunity] = useState(null);
  const [body, setBody] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const [perfumeData, reviewData, communityData] = await Promise.all([
      getPerfume(id),
      listPerfumeReviews(id),
      getCommunity(id),
    ]);
    setPerfume(perfumeData);
    setReviews(reviewData.results || []);
    setCommunity(communityData);
  }

  useEffect(() => {
    load().catch(() => setMessage(t("common.error")));
  }, [id]);

  if (!perfume) {
    return (
      <div className="d-flex align-items-center gap-2">
        <Spinner animation="border" size="sm" />
        <span>{t("common.loading")}</span>
      </div>
    );
  }

  async function handleRating(sentiment) {
    setCommunity(await setRating(id, sentiment));
  }

  async function handleOccasion(occasion) {
    const selected = !community.my_occasions.includes(occasion);
    setCommunity(await setOccasion(id, occasion, selected));
  }

  async function handleReview(event) {
    event.preventDefault();
    await createPerfumeReview(id, body);
    setBody("");
    await load();
  }

  return (
    <>
      <Link to="/" className="d-inline-block mb-3">
        ← {t("nav.home")}
      </Link>
      {message && <Alert variant="warning">{message}</Alert>}
      <Row className="g-4 mb-5">
        <Col md={5}>
          <Image src={perfume.image_url} alt={perfume.name} fluid className="rounded shadow-sm perfume-detail-image" />
        </Col>
        <Col md={7}>
          <p className="text-body-secondary mb-1">{perfume.brand}</p>
          <h1 className="h2">{perfume.name}</h1>
          <p>{perfume.description}</p>
          <p className="h4">${Number(perfume.price).toFixed(2)}</p>
          {isAuthenticated && (
            <Button variant="dark" onClick={() => addItem(perfume.id)}>
              {t("home.addToCart")}
            </Button>
          )}
        </Col>
      </Row>

      <section className="mb-5">
        <h2 className="h4 mb-3">{t("perfume.ratings")}</h2>
        {!isAuthenticated && <p className="text-body-secondary">{t("perfume.loginToParticipate")}</p>}
        <div className="d-flex flex-wrap gap-2">
          {SENTIMENTS.map((sentiment) => (
            <Button
              key={sentiment}
              variant={community?.my_sentiment === sentiment ? "dark" : "outline-secondary"}
              onClick={() => isAuthenticated && handleRating(sentiment)}
              disabled={!isAuthenticated}
            >
              {t(`sentiment.${sentiment}`)}{" "}
              <Badge bg="secondary">{community?.rating_counts?.[sentiment] || 0}</Badge>
            </Button>
          ))}
        </div>
      </section>

      <section className="mb-5">
        <h2 className="h4 mb-3">{t("perfume.occasions")}</h2>
        <div className="d-flex flex-wrap gap-2">
          {OCCASIONS.map((occasion) => (
            <Button
              key={occasion}
              variant={community?.my_occasions?.includes(occasion) ? "dark" : "outline-secondary"}
              onClick={() => isAuthenticated && handleOccasion(occasion)}
              disabled={!isAuthenticated}
            >
              {t(`occasion.${occasion}`)}{" "}
              <Badge bg="secondary">{community?.occasion_counts?.[occasion] || 0}</Badge>
            </Button>
          ))}
        </div>
      </section>

      <section>
        <h2 className="h4 mb-3">{t("perfume.reviews")}</h2>
        {isAuthenticated && (
          <Form className="mb-4" onSubmit={handleReview}>
            <Form.Group className="mb-2">
              <Form.Label>{t("perfume.writeReview")}</Form.Label>
              <Form.Control as="textarea" rows={3} value={body} onChange={(event) => setBody(event.target.value)} required />
            </Form.Group>
            <Button type="submit" variant="dark">
              {t("perfume.sendReview")}
            </Button>
          </Form>
        )}
        {reviews.length === 0 && <p className="text-body-secondary">{t("home.noReviews")}</p>}
        {reviews.map((review) => (
          <div key={review.id} className="border-bottom py-3">
            <strong>{review.username}</strong>
            <div className="small text-body-secondary">{formatDate(review.created_at, i18n.language)}</div>
            <p className="mb-0 mt-2">{review.body}</p>
          </div>
        ))}
      </section>
    </>
  );
}
