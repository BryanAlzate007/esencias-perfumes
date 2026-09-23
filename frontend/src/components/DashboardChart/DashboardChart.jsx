import { useTranslation } from "react-i18next";
import "./DashboardChart.css";

function formatLabel(value, period, language) {
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(year, month - 1, day || 1);
  if (period === "month") {
    return date.toLocaleDateString(language, { month: "short" });
  }
  return String(date.getDate());
}

export default function DashboardChart({ title, points, period, onPeriod }) {
  const { t, i18n } = useTranslation();
  const language = (i18n.resolvedLanguage || i18n.language || "es").startsWith("en") ? "en" : "es";
  const max = Math.max(1, ...points.map((point) => point.value));
  const total = points.reduce((sum, point) => sum + point.value, 0);

  return (
    <section className="dashboard-chart">
      <div className="dashboard-chart-header">
        <div>
          <h2 className="dashboard-chart-title">{title}</h2>
          <p className="dashboard-chart-meta">
            {period === "day" ? t("admin.dayRange") : t("admin.monthRange")}
            <span>{t("admin.chartTotal", { count: total })}</span>
          </p>
        </div>
        <div className="dashboard-chart-filters" role="group" aria-label={title}>
          <button
            type="button"
            className={`dashboard-chart-filter${period === "day" ? " is-active" : ""}`}
            aria-pressed={period === "day"}
            onClick={() => onPeriod("day")}
          >
            {t("admin.byDay")}
          </button>
          <button
            type="button"
            className={`dashboard-chart-filter${period === "month" ? " is-active" : ""}`}
            aria-pressed={period === "month"}
            onClick={() => onPeriod("month")}
          >
            {t("admin.byMonth")}
          </button>
        </div>
      </div>
      <div className="dashboard-bars" role="img" aria-label={`${title}: ${total}`}>
        {points.map((point) => (
          <div className="dashboard-bar" key={point.date} title={`${point.date}: ${point.value}`}>
            <div className="dashboard-bar-track">
              <div className="dashboard-bar-fill" style={{ height: `${(point.value / max) * 100}%` }} />
            </div>
            <span className="dashboard-bar-label">{formatLabel(point.date, period, language)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
