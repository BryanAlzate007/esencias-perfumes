import { useTranslation } from "react-i18next";

export default function CandlesClosing() {
  const { t } = useTranslation();

  return (
    <section className="candles-closing">
      <h2>{t("candlesPage.closingTitle")}</h2>
      <p>{t("candlesPage.closingBody")}</p>
      <a className="candles-button" href="#coleccion">{t("candlesPage.closingCta")}</a>
    </section>
  );
}
