import { useTranslation } from "react-i18next";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import { ClockIcon, HeartIcon } from "./VoteIcons";
import "./VotePanels.css";

const SENTIMENTS = [
  { key: "love", color: "#ef8b7a", emoji: "😍" },
  { key: "like", color: "#d4539a", emoji: "😊" },
  { key: "neutral", color: "#d45b5b", emoji: "😐" },
  { key: "dislike", color: "#5b6ea8", emoji: "🙁" },
  { key: "hate", color: "#8b97ad", emoji: "😠" },
];

const OCCASIONS = [
  { key: "winter", color: "#5ec8dc", emoji: "❄️" },
  { key: "spring", color: "#62c46c", emoji: "🍃" },
  { key: "summer", color: "#e27575", emoji: "☂️" },
  { key: "autumn", color: "#e0a03a", emoji: "🍁" },
  { key: "day", color: "#f0a024", emoji: "☀️" },
  { key: "night", color: "#5b86c7", emoji: "🌙" },
];

function maxCount(counts, keys) {
  return Math.max(1, ...keys.map((item) => counts?.[item.key] || 0));
}

function VoteOption({ item, count, max, selected, label, onSelect }) {
  const ratio = count / max;
  const active = count > 0 && ratio >= 0.2;

  return (
    <button
      type="button"
      className={`vote-option${selected ? " is-selected" : ""}${active ? " is-active" : ""}`}
      style={{ "--vote-color": item.color }}
      onClick={() => onSelect(item.key)}
    >
      <span className="vote-option-icon" aria-hidden="true">
        {item.emoji}
      </span>
      <span className="vote-option-label">{label}</span>
      <span className="vote-meter" aria-hidden="true">
        <span className="vote-meter-fill" style={{ width: `${Math.max(ratio * 100, count > 0 ? 8 : 0)}%` }} />
      </span>
      <span className="vote-option-count">{count}</span>
    </button>
  );
}

export default function VotePanels({ community, onRate, onOccasion }) {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const { openLogin } = useAuthModal();
  const ratingCounts = community?.rating_counts || {};
  const occasionCounts = community?.occasion_counts || {};
  const ratingMax = maxCount(ratingCounts, SENTIMENTS);
  const occasionMax = maxCount(occasionCounts, OCCASIONS);

  function requireAuth(action) {
    if (!isAuthenticated) {
      openLogin(window.location.pathname);
      return;
    }
    action();
  }

  return (
    <div className="vote-panels">
      <section className="vote-card">
        <h2 className="vote-card-title">
          <HeartIcon className="vote-card-title-icon vote-card-title-icon-heart" />
          {t("perfume.ratings")}
        </h2>
        <div className="vote-options">
          {SENTIMENTS.map((item) => (
            <VoteOption
              key={item.key}
              item={item}
              count={ratingCounts[item.key] || 0}
              max={ratingMax}
              selected={community?.my_sentiment === item.key}
              label={t(`sentiment.${item.key}`)}
              onSelect={(key) => requireAuth(() => onRate(key))}
            />
          ))}
        </div>
      </section>

      <section className="vote-card">
        <h2 className="vote-card-title">
          <ClockIcon className="vote-card-title-icon vote-card-title-icon-clock" />
          {t("perfume.occasions")}
        </h2>
        <div className="vote-options">
          {OCCASIONS.map((item) => (
            <VoteOption
              key={item.key}
              item={item}
              count={occasionCounts[item.key] || 0}
              max={occasionMax}
              selected={community?.my_occasions?.includes(item.key)}
              label={t(`occasion.${item.key}`)}
              onSelect={(key) => requireAuth(() => onOccasion(key))}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
