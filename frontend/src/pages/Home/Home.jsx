import { useEffect, useState } from "react";
import { Alert, Container, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import AddToCartModal from "../../components/AddToCardModal/AddToCardModal";
import AdvisorModal from "../../components/AdvisorModal/AdvisorModal";
import PerfumeCard from "../../components/PerfumeCard/PerfumeCard";
import { sendContact } from "../../services/contact";
import { listPerfumePage, PERFUME_PAGE_SIZE } from "../../services/perfumes";
import heroImage from "../../assets/hero-perfume.jpg";
import "./Home.css";

const FALLBACK_BRANDS = ["Esencias", "Maison Luna", "Costa Atelier", "Atelier Norte", "Velmont", "Ambre Royal"];

const CATALOGS = [
  { value: "caballero", labelKey: "admin.catalogCaballero" },
  { value: "dama", labelKey: "admin.catalogDama" },
  { value: "arabe", labelKey: "admin.catalogArabe" },
];

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function pageItems(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => index + 1);
  }
  const items = [1];
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);
  if (start > 2) {
    items.push("start");
  }
  for (let number = start; number <= end; number += 1) {
    items.push(number);
  }
  if (end < total - 1) {
    items.push("end");
  }
  items.push(total);
  return items;
}

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [draftPerfumeId, setDraftPerfumeId] = useState(null);
  const [perfumes, setPerfumes] = useState([]);
  const [total, setTotal] = useState(0);
  const [filtered, setFiltered] = useState(false);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("");
  const [catalogFilter, setCatalogFilter] = useState("");
  const [contact, setContact] = useState({ name: "", email: "", phone: "", message: "" });
  const [contactSent, setContactSent] = useState(false);
  const [contactSending, setContactSending] = useState(false);
  const [contactError, setContactError] = useState("");

  const pageCount = filtered ? 1 : Math.max(1, Math.ceil(total / PERFUME_PAGE_SIZE));

  useEffect(() => {
    const term = query.trim();
    const isFiltered = Boolean(catalogFilter || term);
    let cancelled = false;
    const timer = window.setTimeout(() => {
      setStatus("loading");
      listPerfumePage({ page, catalog: catalogFilter, search: term })
        .then((data) => {
          if (cancelled) {
            return;
          }
          setPerfumes(data.results);
          setTotal(data.count);
          setFiltered(data.filtered || isFiltered);
          setStatus("ready");
        })
        .catch(() => {
          if (!cancelled) {
            setStatus("error");
          }
        });
    }, term ? 300 : 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [page, catalogFilter, query]);

  useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (status !== "ready" || !hash) {
      return;
    }
    requestAnimationFrame(() => scrollToId(hash));
  }, [status]);

  function handleAdd(id) {
    setMessage("");
    setDraftPerfumeId(id);
  }

  function handleQuery(event) {
    setQuery(event.target.value);
    setPage(1);
  }

  function handleCatalog(value) {
    setCatalogFilter((current) => (current === value ? "" : value));
    setPage(1);
  }

  function handlePage(nextPage) {
    setPage(nextPage);
    scrollToId("coleccion");
  }

  const brands = [...new Set([...(perfumes.map((item) => item.brand) || []), ...FALLBACK_BRANDS])];
  const marqueeBrands = [...brands, ...brands];

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
    <div className="home-page">
      <AdvisorModal onWeb={() => navigate("/asesoria")} />
      <AddToCartModal
        perfumeId={draftPerfumeId}
        show={draftPerfumeId != null}
        onHide={() => setDraftPerfumeId(null)}
        onAdded={() => setMessage(t("home.added"))}
      />
      <section className="home-hero" style={{ backgroundImage: `url(${heroImage})` }}>
        <div className="home-hero-overlay">
          <h1 className="home-hero-brand">{t("app.name")}</h1>
          <p className="home-hero-title">{t("home.heroPhrase")}</p>
          <div className="home-hero-actions">
            <button type="button" className="home-ghost-button home-ghost-button-solid" onClick={() => scrollToId("coleccion")}>
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
          <div className="home-catalog-toolbar">
            <input
              type="search"
              className="home-catalog-search"
              value={query}
              onChange={handleQuery}
              placeholder={t("admin.searchPerfumes")}
              aria-label={t("admin.searchPerfumes")}
            />
            <div className="home-catalog-filters" role="group" aria-label={t("admin.perfumeCatalog")}>
              {CATALOGS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  className={`home-catalog-filter${catalogFilter === item.value ? " is-active" : ""}`}
                  aria-pressed={catalogFilter === item.value}
                  onClick={() => handleCatalog(item.value)}
                >
                  {t(item.labelKey)}
                </button>
              ))}
            </div>
          </div>
          {message && <Alert variant="dark" className="mt-3">{message}</Alert>}
          {status === "loading" && (
            <div className="d-flex align-items-center gap-2 text-light mt-4">
              <Spinner animation="border" size="sm" />
              <span>{t("common.loading")}</span>
            </div>
          )}
          {status === "error" && <Alert variant="warning" className="mt-3">{t("common.error")}</Alert>}
          {status === "ready" && perfumes.length === 0 && (
            <Alert variant="dark" className="mt-3">{filtered ? t("admin.noMatches") : t("home.empty")}</Alert>
          )}
          <div className="essence-grid">
            {status === "ready" && perfumes.map((perfume, index) => (
              <PerfumeCard
                key={perfume.id}
                perfume={perfume}
                index={filtered ? index : (page - 1) * PERFUME_PAGE_SIZE + index}
                showCart
                onAddToCart={handleAdd}
              />
            ))}
          </div>
          {status === "ready" && !filtered && pageCount > 1 && (
            <nav className="home-pager" aria-label={t("home.pages")}>
              <button
                type="button"
                className="home-pager-button"
                onClick={() => handlePage(page - 1)}
                disabled={page === 1}
              >
                {t("home.pagePrev")}
              </button>
              {pageItems(page, pageCount).map((item) =>
                typeof item === "number" ? (
                  <button
                    key={item}
                    type="button"
                    className={`home-pager-button${item === page ? " is-active" : ""}`}
                    aria-current={item === page ? "page" : undefined}
                    onClick={() => handlePage(item)}
                  >
                    {item}
                  </button>
                ) : (
                  <span key={item} className="home-pager-gap" aria-hidden="true">
                    …
                  </span>
                ),
              )}
              <button
                type="button"
                className="home-pager-button"
                onClick={() => handlePage(page + 1)}
                disabled={page === pageCount}
              >
                {t("home.pageNext")}
              </button>
            </nav>
          )}
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
    </div>
  );
}
