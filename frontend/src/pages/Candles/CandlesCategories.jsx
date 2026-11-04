import { useTranslation } from "react-i18next";
import { CANDLE_STYLES } from "./candleMedia";
import { useReveal } from "./useReveal";

export default function CandlesCategories({ style, onSelect }) {
  const { t } = useTranslation();
  const [ref, shown] = useReveal();

  return (
    <section id="estilos" className={`candles-styles${shown ? " is-shown" : ""}`} ref={ref} aria-labelledby="candles-styles-title">
      <div className="candles-section-head">
        <h2 id="candles-styles-title">{t("candlesPage.stylesTitle")}</h2>
      </div>
      <div className="candles-style-grid">
        {CANDLE_STYLES.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`candles-style${style === item.id ? " is-active" : ""}`}
            aria-pressed={style === item.id}
            onClick={() => onSelect(item.id)}
          >
            <img src={item.image} alt="" />
            <span className="candles-style-copy">
              <strong>{t(`candlesPage.styles.${item.id}`)}</strong>
              <span>{t(`candlesPage.styleCopy.${item.id}`)}</span>
              <em>{t("candlesPage.enter")}</em>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
