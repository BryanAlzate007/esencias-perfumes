import { useTranslation } from "react-i18next";
import { candleImages } from "./candleMedia";
import { useReveal } from "./useReveal";

function lines(value) {
  return String(value).split("\n");
}

export default function CandlesEditorial() {
  const { t } = useTranslation();
  const [ref, shown] = useReveal();

  return (
    <section id="historia" className={`candles-editorial${shown ? " is-shown" : ""}`} ref={ref}>
      <figure className="candles-editorial-media">
        <img src={candleImages.manifesto} alt={t("candlesPage.manifestoAlt")} />
      </figure>
      <div className="candles-editorial-copy">
        <h2>
          {lines(t("candlesPage.manifestoTitle")).map((line) => (
            <span key={line}>{line}</span>
          ))}
        </h2>
        <p>{t("candlesPage.manifestoBody")}</p>
        <a className="candles-link" href="#experiencia">{t("candlesPage.manifestoCta")}</a>
      </div>
    </section>
  );
}
