import { useTranslation } from "react-i18next";
import { candleImages } from "./candleMedia";
import { useReveal } from "./useReveal";

function lines(value) {
  return String(value).split("\n");
}

export default function CandlesGifting() {
  const { t } = useTranslation();
  const [ref, shown] = useReveal();

  return (
    <section id="regalos" className={`candles-gift${shown ? " is-shown" : ""}`} ref={ref}>
      <figure>
        <img src={candleImages.gift} alt={t("candlesPage.giftAlt")} />
      </figure>
      <div>
        <h2>
          {lines(t("candlesPage.giftTitle")).map((line) => (
            <span key={line}>{line}</span>
          ))}
        </h2>
        <p>{t("candlesPage.giftBody")}</p>
        <a className="candles-button" href="#coleccion">{t("candlesPage.giftCta")}</a>
      </div>
    </section>
  );
}
