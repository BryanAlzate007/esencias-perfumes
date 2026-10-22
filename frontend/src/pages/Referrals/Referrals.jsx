import { useEffect, useState } from "react";
import { Alert, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { mediaUrl } from "../../lib/media";
import { getReferrals } from "../../services/referrals";
import "./Referrals.css";

export default function Referrals() {
  const { t, i18n } = useTranslation();
  const { refreshUser } = useAuth();
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getReferrals()
      .then(async (data) => {
        if (!cancelled) {
          setOverview(data);
        }
        await refreshUser();
      })
      .catch(() => {
        if (!cancelled) {
          setError(t("referrals.loadError"));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [refreshUser, t]);

  if (loading) {
    return (
      <div className="referrals-page referrals-loading">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="referrals-page">
        <Alert variant="danger">{error || t("referrals.loadError")}</Alert>
      </div>
    );
  }

  if (!overview.enabled) {
    return (
      <div className="referrals-page">
        <p className="referrals-kicker">{t("referrals.kicker")}</p>
        <h1 className="referrals-title">{t("referrals.title")}</h1>
        <p className="referrals-lead">{t("referrals.lead")}</p>
        <Link to="/#coleccion" className="referrals-start">
          {t("referrals.start")}
        </Link>
      </div>
    );
  }

  return (
    <div className="referrals-page">
      <div className="referrals-share">
        <article className="referrals-card">
          <p className="referrals-kicker">{t("referrals.shareKicker")}</p>
          <h1 className="referrals-user">{overview.username}</h1>
          {overview.qr_url && (
            <img src={mediaUrl(overview.qr_url)} alt={t("referrals.qrAlt")} />
          )}
          <p className="referrals-code">{overview.code}</p>
        </article>
      </div>
      <h2 className="referrals-list-title">{t("referrals.listTitle")}</h2>
      {overview.referrals.length === 0 ? (
        <p className="referrals-empty">{t("referrals.empty")}</p>
      ) : (
        <ul className="referrals-list">
          {overview.referrals.map((person) => (
            <li key={`${person.username}-${person.purchased_at}`}>
              <span>{person.username}</span>
              <time dateTime={person.purchased_at}>
                {new Intl.DateTimeFormat(i18n.language, { dateStyle: "medium" }).format(new Date(person.purchased_at))}
              </time>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
