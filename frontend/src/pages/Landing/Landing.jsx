import { Container } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import ContactSection from "../../components/ContactSection/ContactSection";
import heroImage from "../../assets/hero-perfume.jpg";
import "../Home/Home.css";

const WORDS = ["Perfumes", "Velas", "Esencias", "Atelier", "Maison"];

export default function Landing() {
  const { t } = useTranslation();
  const marquee = [...WORDS, ...WORDS];

  return (
    <div className="home-page">
      <section className="home-hero" style={{ backgroundImage: `url(${heroImage})` }}>
        <div className="home-hero-overlay">
          <h1 className="home-hero-brand">{t("app.name")}</h1>
          <p className="home-hero-title">{t("landing.heroPhrase")}</p>
          <div className="landing-gates">
            <Link to="/perfumes" className="landing-gate">
              <span className="home-kicker">{t("landing.perfumesKicker")}</span>
              <h2>{t("landing.perfumesTitle")}</h2>
              <p>{t("landing.perfumesLead")}</p>
            </Link>
            <Link to="/candles" className="landing-gate">
              <span className="home-kicker">{t("landing.candlesKicker")}</span>
              <h2>{t("landing.candlesTitle")}</h2>
              <p>{t("landing.candlesLead")}</p>
            </Link>
          </div>
        </div>
        <div className="home-marquee" aria-hidden="true">
          <div className="home-marquee-track">
            {marquee.map((word, index) => (
              <span key={`${word}-${index}`} className="home-marquee-item">
                {word}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section id="historia" className="home-section home-story">
        <Container className="home-story-inner">
          <p className="home-kicker">{t("landing.storyKicker")}</p>
          <h2 className="home-section-title">{t("landing.storyTitle")}</h2>
          <p className="home-story-text">{t("landing.storyLead")}</p>
          <p className="home-story-copy">{t("landing.storyBody")}</p>
        </Container>
      </section>

      <ContactSection />
    </div>
  );
}
