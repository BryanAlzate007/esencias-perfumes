import { useTranslation } from "react-i18next";
import { CANDLE_ROOMS, candleImages } from "./candleMedia";
import { useReveal } from "./useReveal";

export default function CandlesExperience({ onSelect }) {
  const { t } = useTranslation();
  const [ref, shown] = useReveal();

  return (
    <section id="experiencia" className={`candles-experience${shown ? " is-shown" : ""}`} ref={ref}>
      <div className="candles-section-head">
        <h2>{t("candlesPage.experienceTitle")}</h2>
      </div>
      <figure className="candles-experience-photo">
        <img src={candleImages.room} alt={t("candlesPage.roomAlt")} />
      </figure>
      <div className="candles-rooms">
        {CANDLE_ROOMS.map((room) => (
          <article key={room.id}>
            <h3>{t(`candlesPage.rooms.${room.id}.title`)}</h3>
            <p>{t(`candlesPage.rooms.${room.id}.body`)}</p>
            <p className="candles-room-scent">{t(`candlesPage.rooms.${room.id}.scent`)}</p>
            <button type="button" className="candles-link" onClick={() => onSelect(room.style)}>
              {t("candlesPage.exploreRelated")}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
