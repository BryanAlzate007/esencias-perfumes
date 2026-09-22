import { useEffect, useState } from "react";
import { Alert, Container, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Navigate } from "react-router-dom";
import PerfumeCard from "../../components/PerfumeCard/PerfumeCard";
import { useAuth } from "../../hooks/useAuth";
import { useAuthModal } from "../../hooks/useAuthModal";
import { useCart } from "../../hooks/useCart";
import { listPerfumes } from "../../services/perfumes";
import heroImage from "../../assets/hero-perfume.jpg";
import "./Home.css";

const FALLBACK_BRANDS = ["Esencias", "Maison Luna", "Costa Atelier", "Atelier Norte", "Velmont", "Ambre Royal"];

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Home() {
  const { t } = useTranslation();
  const { isAdmin, isAuthenticated } = useAuth();
  const { openLogin } = useAuthModal();
  const { addItem } = useCart();
  const [perfumes, setPerfumes] = useState([]);
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  const [contact, setContact] = useState({ name: "", email: "", message: "" });
  const [contactSent, setContactSent] = useState(false);

  useEffect(() => {
    listPerfumes()
      .then((data) => {
        setPerfumes(data.results || []);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (status !== "ready" || !hash) {
      return;
    }
    requestAnimationFrame(() => scrollToId(hash));
  }, [status]);

  if (isAdmin) {
    return <Navigate to="/admin/catalogo" replace />;
  }

  async function handleAdd(id) {
    if (!isAuthenticated) {
      setMessage(t("cart.loginRequired"));
      openLogin("/");
      return;
    }
    await addItem(id);
    setMessage(t("home.added"));
  }

  const brands = [...new Set([...(perfumes.map((item) => item.brand) || []), ...FALLBACK_BRANDS])];
  const marqueeBrands = [...brands, ...brands];

  function handleContact(event) {
    event.preventDefault();
    setContactSent(true);
  }

  return (
    <div className="home-page">
      <section className="home-hero" style={{ backgroundImage: `url(${heroImage})` }}>
        <div className="home-hero-overlay">
          <p className="home-kicker">{t("app.name")}</p>
          <h1 className="home-hero-title">{t("home.heroPhrase")}</h1>
          <div className="home-hero-actions">
            <button type="button" className="home-ghost-button" onClick={() => scrollToId("coleccion")}>
              {t("home.collectionCta")}
            </button>
            <button type="button" className="home-ghost-button" onClick={() => scrollToId("historia")}>
              {t("home.storyCta")}
            </button>
          </div>
        </div>
        <div className="home-marquee" aria-hidden="true">
          <div className="home-marquee-track">
            {marqueeBrands.map((brand, index) => (
              <span key={`${brand}-${index}`} className="home-marquee-item">
                {brand}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section id="coleccion" className="home-section home-collection">
        <Container>
          <p className="home-kicker">{t("home.collectionKicker")}</p>
          <h2 className="home-section-title">{t("home.collectionTitle")}</h2>
          {message && <Alert variant="dark" className="mt-3">{message}</Alert>}
          {status === "loading" && (
            <div className="d-flex align-items-center gap-2 text-light mt-4">
              <Spinner animation="border" size="sm" />
              <span>{t("common.loading")}</span>
            </div>
          )}
          {status === "error" && <Alert variant="warning" className="mt-3">{t("common.error")}</Alert>}
          {status === "ready" && perfumes.length === 0 && (
            <Alert variant="dark" className="mt-3">{t("home.empty")}</Alert>
          )}
          <div className="essence-grid">
            {perfumes.map((perfume, index) => (
              <PerfumeCard
                key={perfume.id}
                perfume={perfume}
                index={index}
                showCart
                onAddToCart={handleAdd}
              />
            ))}
          </div>
        </Container>
      </section>

      <section id="historia" className="home-section home-story">
        <Container className="home-story-inner">
          <p className="home-kicker">{t("home.storyKicker")}</p>
          <h2 className="home-section-title">{t("home.storyTitle")}</h2>
          <p className="home-story-text">{t("home.storyLead")}</p>
          <p className="home-story-copy">{t("home.storyBody")}</p>
        </Container>
      </section>

      <section id="contacto" className="home-section home-contact">
        <Container>
          <p className="home-kicker">{t("home.contactKicker")}</p>
          <h2 className="home-section-title">{t("home.contactTitle")}</h2>
          <p className="home-contact-copy">{t("home.contactLead")}</p>
          {contactSent ? (
            <Alert variant="success" className="mt-4">{t("home.contactSent")}</Alert>
          ) : (
            <form className="home-contact-form" onSubmit={handleContact}>
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
                {t("home.contactMessage")}
                <textarea
                  rows={4}
                  required
                  value={contact.message}
                  onChange={(event) => setContact((current) => ({ ...current, message: event.target.value }))}
                />
              </label>
              <button type="submit" className="home-ghost-button home-ghost-button-solid">
                {t("home.contactSend")}
              </button>
            </form>
          )}
        </Container>
      </section>
    </div>
  );
}
