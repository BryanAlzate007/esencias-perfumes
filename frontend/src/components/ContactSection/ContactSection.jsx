import { useState } from "react";
import { Alert, Container } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { sendContact } from "../../services/contact";

export default function ContactSection() {
  const { t } = useTranslation();
  const [contact, setContact] = useState({ name: "", email: "", phone: "", message: "" });
  const [contactSent, setContactSent] = useState(false);
  const [contactSending, setContactSending] = useState(false);
  const [contactError, setContactError] = useState("");

  async function handleContact(event) {
    event.preventDefault();
    setContactError("");
    setContactSending(true);
    try {
      await sendContact(contact);
      setContactSent(true);
    } catch (requestError) {
      setContactError(requestError?.response?.data?.detail || t("home.contactError"));
    } finally {
      setContactSending(false);
    }
  }

  return (
    <section id="contacto" className="home-section home-contact">
      <Container>
        <p className="home-kicker">{t("home.contactKicker")}</p>
        <h2 className="home-section-title">{t("home.contactTitle")}</h2>
        <p className="home-contact-copy">{t("home.contactLead")}</p>
        {contactSent ? (
          <Alert variant="success" className="mt-4">{t("home.contactSent")}</Alert>
        ) : (
          <form className="home-contact-form" onSubmit={handleContact}>
            {contactError && <Alert variant="danger">{contactError}</Alert>}
            <label>
              {t("auth.name")}
              <input
                required
                value={contact.name}
                onChange={(event) => setContact((current) => ({ ...current, name: event.target.value }))}
              />
            </label>
            <label>
              {t("auth.email")}
              <input
                type="email"
                required
                value={contact.email}
                onChange={(event) => setContact((current) => ({ ...current, email: event.target.value }))}
              />
            </label>
            <label>
              {t("home.contactPhone")}
              <input
                type="tel"
                required
                autoComplete="tel"
                placeholder={t("home.contactPhonePlaceholder")}
                value={contact.phone}
                onChange={(event) => setContact((current) => ({ ...current, phone: event.target.value }))}
              />
            </label>
            <label>
              {t("home.contactMessage")}
              <textarea
                rows={4}
                required
                value={contact.message}
                onChange={(event) => setContact((current) => ({ ...current, message: event.target.value }))}
              />
            </label>
            <button type="submit" className="home-ghost-button home-ghost-button-solid" disabled={contactSending}>
              {contactSending ? t("home.contactSending") : t("home.contactSend")}
            </button>
          </form>
        )}
      </Container>
    </section>
  );
}
