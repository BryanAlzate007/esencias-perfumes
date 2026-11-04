import { useTranslation } from "react-i18next";
import { candleImages } from "./candleMedia";

function lines(value) {
  return String(value).split("\n");
}

export default function CandlesHero() {
  const { t } = useTranslation();

  return (
    <section className="candles-hero" aria-labelledby="candles-hero-title">
      <img className="candles-hero-photo" src={candleImages.hero} alt={t("candlesPage.heroAlt")} />
      <div className="candles-hero-shade" />
      <div className="candles-hero-copy">
        <p className="candles-kicker">{t("candlesPage.kicker")}</p>
        <h1 id="candles-hero-title" className="candles-hero-title">
          {lines(t("candlesPage.heroTitle")).map((line) => (
            <span key={line}>{line}</span>
          ))}
        </h1>
        <p className="candles-hero-lead">
          {lines(t("candlesPage.heroLead")).map((line) => (
            <span key={line}>{line}</span>
          ))}
        </p>
        <div className="candles-hero-actions">
          <a className="candles-button" href="#coleccion">{t("candlesPage.explore")}</a>
          <a className="candles-button candles-button-ghost" href="#estilos">{t("candlesPage.discover")}</a>
        </div>
      </div>
      <a className="candles-scroll" href="#historia">
        <span>{t("candlesPage.scroll")}</span>
      </a>
    </section>
  );
}
