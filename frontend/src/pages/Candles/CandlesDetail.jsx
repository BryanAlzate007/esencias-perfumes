import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

export default function CandlesDetail({ piece, onClose, onDemo }) {
  const { t } = useTranslation();
  const closeRef = useRef(null);
  const [said, setSaid] = useState(false);

  useEffect(() => {
    if (!piece) {
      return undefined;
    }
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    function onKey(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }
    document.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener("keydown", onKey);
    };
  }, [piece, onClose]);

  if (!piece) {
    return null;
  }

  return (
    <div className="candles-detail" role="presentation" onClick={onClose}>
      <article
        className="candles-detail-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="candles-detail-title"
        onClick={(event) => event.stopPropagation()}
      >
        <img src={piece.image} alt="" />
        <div>
          <p className="candles-kicker">{t("candlesPage.demoNote")}</p>
          <h2 id="candles-detail-title">{piece.name}</h2>
          <p>{t(`candlesPage.categories.${piece.style}`)}</p>
          <p className="candles-detail-price">
            <span>{t("candlesPage.illustrativePrice")}</span>
            {piece.price}
          </p>
          <p>{t("candlesPage.available")}</p>
          <div className="candles-hero-actions">
            <button
              type="button"
              className="candles-button"
              onClick={() => {
                onDemo(piece);
                setSaid(true);
              }}
            >
              {t("candlesPage.add")}
            </button>
            <button type="button" className="candles-button candles-button-ghost" onClick={onClose} ref={closeRef}>
              {t("candlesPage.close")}
            </button>
          </div>
          {said && <p role="status">{t("candlesPage.demoAdded", { name: piece.name })}</p>}
        </div>
      </article>
    </div>
  );
}
