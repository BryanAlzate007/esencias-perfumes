import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { sendContact } from "../../services/contact";
import { CANDLE_STYLES } from "./candleMedia";
import "./Candles.css";

export default function CandlesFooter({ onSelect }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", message: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  function update(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setStatus("sending");
    setError("");
    try {
      await sendContact(form);
      setStatus("sent");
    } catch (requestError) {
      setStatus("idle");
      setError(requestError?.response?.data?.detail || t("candlesPage.newsletterError"));
    }
  }

  function chooseStyle(id) {
    if (onSelect) {
      onSelect(id);
      return;
    }
    navigate(`/candles?estilo=${id}`);
  }

  return (
    <footer id="contacto" className="candles-footer">
      <div className="candles-footer-brand">
        <p className="candles-footer-logo">{t("app.name")}</p>
        <p>{t("candlesPage.kicker")}</p>
      </div>
      <nav aria-label={t("candlesPage.footerNav")}>
        <p>{t("candlesPage.footerNav")}</p>
        <Link to="/">{t("nav.home")}</Link>
        <Link to="/perfumes">{t("nav.perfumes")}</Link>
        <Link to="/candles">{t("nav.candles")}</Link>
        <a href="#historia">{t("home.storyCta")}</a>
      </nav>
      <div>
        <p>{t("candlesPage.footerStyles")}</p>
        {CANDLE_STYLES.map((item) => (
          <button key={item.id} type="button" onClick={() => chooseStyle(item.id)}>
            {t(`candlesPage.styles.${item.id}`)}
          </button>
        ))}
      </div>
      <div>
        <p>{t("candlesPage.footerSocial")}</p>
        <p className="candles-footer-note">{t("candlesPage.footerSocialNote")}</p>
        <p>{t("candlesPage.footerLegal")}</p>
        <Link to="/politica-de-privacidad">{t("nav.privacy")}</Link>
      </div>
      <form className="candles-newsletter" onSubmit={submit}>
        <p>{t("candlesPage.newsletter")}</p>
        <p className="candles-footer-note">{t("candlesPage.newsletterLead")}</p>
        {status === "sent" ? (
          <p role="status">{t("candlesPage.newsletterSent")}</p>
        ) : (
          <>
            {error && <p role="alert">{error}</p>}
            <label>
              {t("candlesPage.newsletterName")}
              <input name="name" required value={form.name} onChange={update} />
            </label>
            <label>
              {t("candlesPage.newsletterEmail")}
              <input name="email" type="email" required autoComplete="email" value={form.email} onChange={update} />
            </label>
            <label>
              {t("candlesPage.newsletterPhone")}
              <input name="phone" type="tel" required autoComplete="tel" value={form.phone} onChange={update} />
            </label>
            <label>
              {t("candlesPage.newsletterMessage")}
              <textarea name="message" required rows={3} value={form.message} onChange={update} />
            </label>
            <button type="submit" className="candles-button" disabled={status === "sending"}>
              {status === "sending" ? t("candlesPage.newsletterSending") : t("candlesPage.newsletterSend")}
            </button>
          </>
        )}
      </form>
    </footer>
  );
}
