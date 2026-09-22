import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import "./PerfumeCard.css";

export default function PerfumeCard({ perfume, index = 0, onAddToCart, showCart = true }) {
  const { t } = useTranslation();
  const number = String(index + 1).padStart(2, "0");
  const notes = perfume.notes || perfume.brand;

  return (
    <article className="essence-card">
      <Link to={`/perfumes/${perfume.id}`} className="essence-card-link">
        <div className="essence-card-media">
          <img src={perfume.image_url} alt={perfume.name} />
          <span className="essence-card-index">No. {number}</span>
        </div>
        <div className="essence-card-body">
          <div className="essence-card-title-row">
            <h3 className="essence-card-name">{perfume.name}</h3>
            <span className="essence-card-price">${Number(perfume.price).toFixed(0)}</span>
          </div>
          <p className="essence-card-notes">{notes}</p>
        </div>
      </Link>
      {showCart && (
        <button
          type="button"
          className="essence-card-button"
          onClick={() => onAddToCart?.(perfume.id)}
        >
          {t("home.addToCart")}
        </button>
      )}
    </article>
  );
}
