import { useEffect, useState } from "react";
import { Alert, Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { deleteReview, listMyReviews } from "../../services/reviews";

export default function Comments() {
  const { t, i18n } = useTranslation();
  const [reviews, setReviews] = useState([]);

  async function load() {
    const data = await listMyReviews();
    setReviews(data.results || []);
  }

  useEffect(() => {
    load().catch(() => setReviews([]));
  }, []);

  async function handleDelete(id) {
    await deleteReview(id);
    await load();
  }

  return (
    <>
      <h1 className="h2 mb-4">{t("comments.title")}</h1>
      {reviews.length === 0 && <Alert variant="light">{t("comments.empty")}</Alert>}
      {reviews.map((review) => (
        <div key={review.id} className="border-bottom py-3 d-flex justify-content-between gap-3">
          <div>
            <Link to={`/perfumes/${review.perfume}`}>{review.perfume_name}</Link>
            <div className="small text-body-secondary">
              {review.username} · {new Intl.DateTimeFormat(i18n.language, { dateStyle: "medium" }).format(new Date(review.created_at))}
            </div>
            <p className="mb-0 mt-2">{review.body}</p>
          </div>
          <Button variant="outline-secondary" size="sm" onClick={() => handleDelete(review.id)}>
            {t("common.delete")}
          </Button>
        </div>
      ))}
    </>
  );
}
