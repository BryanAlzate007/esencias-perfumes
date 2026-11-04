import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import AddToCartModal from "../../components/AddToCardModal/AddToCardModal";
import PerfumeCard from "../../components/PerfumeCard/PerfumeCard";
import { listPerfumePage } from "../../services/perfumes";
import { DEMO_CANDLES } from "./candleMedia";
import { useReveal } from "./useReveal";

export default function CandlesCollection({ style, notice, onOpen, onDemo, onClear }) {
  const { t } = useTranslation();
  const [ref, shown] = useReveal();
  const [catalog, setCatalog] = useState([]);
  const [catalogStatus, setCatalogStatus] = useState("loading");
  const [cartId, setCartId] = useState(null);
  const [cartMessage, setCartMessage] = useState("");
  const pieces = style ? DEMO_CANDLES.filter((piece) => piece.style === style) : DEMO_CANDLES;

  useEffect(() => {
    let cancelled = false;
    listPerfumePage({ kind: "candle" })
      .then((data) => {
        if (cancelled) {
          return;
        }
        setCatalog((data.results || []).filter((item) => item.kind === "candle"));
        setCatalogStatus("ready");
      })
      .catch(() => {
        if (!cancelled) {
          setCatalogStatus("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section id="coleccion" className={`candles-collection${shown ? " is-shown" : ""}`} ref={ref}>
      <AddToCartModal
        perfumeId={cartId}
        show={cartId != null}
        onHide={() => setCartId(null)}
        onAdded={() => setCartMessage(t("home.added"))}
      />
      <div className="candles-section-head">
        <h2>{t("candlesPage.collectionTitle")}</h2>
        <p>{t("candlesPage.collectionLead")}</p>
        <p className="candles-demo-note">{t("candlesPage.demoNote")}</p>
        {style && (
          <p className="candles-filter-note">
            {t("candlesPage.filterNote")}
            {" "}
            <button type="button" className="candles-link" onClick={onClear}>
              {t("candlesPage.clearFilter")}
            </button>
          </p>
        )}
        {notice && <p className="candles-status" role="status">{notice}</p>}
      </div>
      <div className="candles-grid">
        {pieces.map((piece, index) => (
          <article className={`candles-piece candles-piece-${index + 1}`} key={`${style || "all"}-${piece.id}`}>
            <button type="button" className="candles-piece-media" onClick={() => onOpen(piece)}>
              <img src={piece.image} alt={piece.name} />
            </button>
            <div className="candles-piece-body">
              <div>
                <h3>{piece.name}</h3>
                <p>{t(`candlesPage.categories.${piece.style}`)}</p>
              </div>
              <p className="candles-piece-price">
                <span>{t("candlesPage.illustrativePrice")}</span>
                {piece.price}
              </p>
              <p className="candles-piece-stock">{t("candlesPage.available")}</p>
              <div className="candles-piece-actions">
                <button type="button" className="candles-button" onClick={() => onDemo(piece)}>
                  {t("candlesPage.add")}
                </button>
                <button type="button" className="candles-link" onClick={() => onOpen(piece)}>
                  {t("candlesPage.details")}
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="candles-live">
        <p className="candles-kicker">{t("candlesPage.catalogKicker")}</p>
        <p>{t("candlesPage.catalogLead")}</p>
        {catalogStatus === "loading" && <p>{t("candlesPage.catalogLoading")}</p>}
        {catalogStatus === "error" && <p role="alert">{t("candlesPage.catalogError")}</p>}
        {catalogStatus === "ready" && catalog.length === 0 && <p>{t("candlesPage.catalogEmpty")}</p>}
        {cartMessage && <p className="candles-status" role="status">{cartMessage}</p>}
        {catalogStatus === "ready" && catalog.length > 0 && (
          <div className="candles-live-grid">
            {catalog.map((perfume, index) => (
              <PerfumeCard
                key={perfume.id}
                perfume={perfume}
                index={index}
                showCart
                onAddToCart={setCartId}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
