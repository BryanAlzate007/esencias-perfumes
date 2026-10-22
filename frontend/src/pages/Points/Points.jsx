import { useEffect, useState } from "react";
import { Alert, Button, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { getPoints, redeemReward } from "../../services/points";
import "./Points.css";

export default function Points() {
  const { t } = useTranslation();
  const { refreshUser } = useAuth();
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [redeemingId, setRedeemingId] = useState(null);

  async function load() {
    const data = await getPoints();
    setOverview(data);
    await refreshUser();
    return data;
  }

  useEffect(() => {
    let cancelled = false;
    load()
      .catch(() => {
        if (!cancelled) {
          setError(t("points.loadError"));
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
  }, [refreshUser]);

  async function handleRedeem(reward) {
    setRedeemingId(reward.id);
    setError("");
    setNotice("");
    try {
      await redeemReward(reward.id);
      await load();
      setNotice(t("points.redeemed", { name: reward.name }));
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || t("common.error"));
    } finally {
      setRedeemingId(null);
    }
  }

  if (loading) {
    return (
      <div className="points-page points-loading">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="points-page">
        <Alert variant="danger">{error || t("points.loadError")}</Alert>
      </div>
    );
  }

  if (!overview.has_purchase) {
    return (
      <div className="points-page">
        <p className="points-kicker">{t("points.kicker")}</p>
        <h1 className="points-title">{t("points.title")}</h1>
        <p className="points-lead">{t("points.lead")}</p>
        <Link to="/#coleccion" className="points-start">
          {t("points.start")}
        </Link>
      </div>
    );
  }

  return (
    <div className="points-page">
      <p className="points-kicker">{t("points.rewardsKicker")}</p>
      <h1 className="points-title">{t("points.rewardsTitle")}</h1>
      <p className="points-lead">{t("points.balance", { count: overview.points })}</p>
      <p className="points-note">{t("points.redeemNote")}</p>
      {error && <Alert variant="danger">{error}</Alert>}
      {notice && <Alert variant="success">{notice}</Alert>}
      {overview.rewards.length === 0 ? (
        <Alert variant="light">{t("points.emptyRewards")}</Alert>
      ) : (
        <div className="points-grid">
          {overview.rewards.map((reward) => (
            <article key={reward.id} className="points-card">
              <span className="points-card-cost">{t("points.cost", { count: reward.points_cost })}</span>
              <h2 className="points-card-title">{reward.name}</h2>
              {reward.description && <p className="points-card-text">{reward.description}</p>}
              <Button
                type="button"
                className="points-redeem"
                disabled={!reward.can_redeem || redeemingId === reward.id}
                onClick={() => handleRedeem(reward)}
              >
                {reward.can_redeem ? t("points.redeem") : t("points.unavailable")}
              </Button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
