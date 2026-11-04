import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";
import { CANDLE_STYLES } from "./candleMedia";
import CandlesCategories from "./CandlesCategories";
import CandlesClosing from "./CandlesClosing";
import CandlesCollection from "./CandlesCollection";
import CandlesDetail from "./CandlesDetail";
import CandlesEditorial from "./CandlesEditorial";
import CandlesExperience from "./CandlesExperience";
import CandlesFooter from "./CandlesFooter";
import CandlesGifting from "./CandlesGifting";
import CandlesHero from "./CandlesHero";
import "./Candles.css";

function scrollToCollection() {
  document.getElementById("coleccion")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function CandlesPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const [style, setStyle] = useState("");
  const [detail, setDetail] = useState(null);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    const previousTitle = document.title;
    document.title = t("candlesPage.metaTitle");
    let description = document.querySelector('meta[name="description"]');
    const created = !description;
    const previousDescription = description?.getAttribute("content") || "";
    if (!description) {
      description = document.createElement("meta");
      description.setAttribute("name", "description");
      document.head.appendChild(description);
    }
    description.setAttribute("content", t("candlesPage.metaDescription"));
    return () => {
      document.title = previousTitle;
      if (created) {
        description.remove();
      } else {
        description.setAttribute("content", previousDescription);
      }
    };
  }, [t]);

  useEffect(() => {
    const estilo = params.get("estilo");
    if (!CANDLE_STYLES.some((item) => item.id === estilo)) {
      return;
    }
    setStyle(estilo);
    requestAnimationFrame(scrollToCollection);
  }, [params]);

  function selectStyle(next) {
    setStyle(next);
    setNotice("");
    scrollToCollection();
  }

  function showDemo(piece) {
    setNotice(t("candlesPage.demoAdded", { name: piece.name }));
  }

  return (
    <main className="candles-page">
      <CandlesHero />
      <CandlesEditorial />
      <CandlesCollection
        style={style}
        notice={notice}
        onOpen={setDetail}
        onDemo={showDemo}
        onClear={() => setStyle("")}
      />
      <CandlesCategories style={style} onSelect={selectStyle} />
      <CandlesExperience onSelect={selectStyle} />
      <CandlesGifting />
      <CandlesClosing />
      <CandlesFooter onSelect={selectStyle} />
      <CandlesDetail key={detail?.id || "closed"} piece={detail} onClose={() => setDetail(null)} onDemo={showDemo} />
    </main>
  );
}
