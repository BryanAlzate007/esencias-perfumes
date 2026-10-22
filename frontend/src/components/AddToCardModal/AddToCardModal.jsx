import { useEffect, useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useCart } from "../../hooks/useCart";
import { mediaUrl } from "../../lib/media";
import { previewQuote } from "../../services/orders";
import { formatMoney } from "../../lib/money";
import "./AddToCardModal.css";

function Stars({ value }) {
  const rounded = Math.round(Number(value) || 0);
  return (
    <p className="add-cart-stars" aria-label={`${rounded} / 5`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span key={star} className={star <= rounded ? "is-on" : "is-off"}>
          ★
        </span>
      ))}
    </p>
  );
}

function OptionCard({ selected, image, name, content, stockLabel, disabled, onSelect }) {
  return (
    <label
      className={selected ? "add-cart-option is-selected" : "add-cart-option"}
      onClick={(event) => {
        event.preventDefault();
        if (!disabled) {
          onSelect();
        }
      }}
    >
      {mediaUrl(image) && <img src={mediaUrl(image)} alt="" />}
      <input type="radio" name="container" checked={selected} onChange={onSelect} disabled={disabled} />
      <span className="add-cart-option-name">{name}</span>
      {content && <span className="add-cart-option-content">{content}</span>}
      <span className="add-cart-stock">{stockLabel}</span>
    </label>
  );
}

export default function AddToCartModal({ perfumeId, show, onHide, onAdded }) {
  const { t, i18n } = useTranslation();
  const { saveQuote } = useCart();
  const [quote, setQuote] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [pricing, setPricing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const quoteRef = useRef(null);
  const requestSeq = useRef(0);

  quoteRef.current = quote;

  useEffect(() => {
    if (!show || !perfumeId) {
      return undefined;
    }
    let active = true;
    setLoading(true);
    setError("");
    setQuote(null);
    setQuantity(1);
    previewQuote({ perfume: perfumeId })
      .then((data) => {
        if (!active) {
          return;
        }
        setQuote(data);
      })
      .catch(() => {
        if (active) {
          setError(t("cart.draftError"));
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [show, perfumeId, t]);

  async function applyQuote(payload) {
    const seq = ++requestSeq.current;
    setPricing(true);
    setError("");
    try {
      const data = await previewQuote({ perfume: perfumeId, ...payload });
      if (seq !== requestSeq.current) {
        return;
      }
      setQuote(data);
    } catch {
      if (seq === requestSeq.current) {
        setError(t("cart.quoteError"));
      }
    } finally {
      if (seq === requestSeq.current) {
        setPricing(false);
      }
    }
  }

  function selectContainer(containerId) {
    const current = quoteRef.current;
    if (!current) {
      return;
    }
    applyQuote({ container: containerId });
  }

  async function handleConfirm() {
    if (!quote) {
      return;
    }
    setSaving(true);
    setError("");
    try {
      const units = Math.max(1, Math.floor(Number(quantity) || 1));
      await saveQuote({ ...quote, quantity: units });
      onAdded?.();
      onHide();
    } catch {
      setError(t("cart.quoteError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal show={show} onHide={onHide} centered scrollable size="lg" className="add-cart-modal">
      <Modal.Header closeButton>
        <Modal.Title>
          {quote?.order_id ? t("cart.orderNumber", { id: quote.order_id }) : t("home.addToCart")}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {loading && (
          <div className="d-flex align-items-center gap-2">
            <Spinner animation="border" size="sm" />
            <span>{t("common.loading")}</span>
          </div>
        )}
        {quote && (
          <div className="add-cart-layout">
            {mediaUrl(quote.perfume.image_url) && (
              <img className="add-cart-lotion" src={mediaUrl(quote.perfume.image_url)} alt={quote.perfume.name} />
            )}
            <div className="add-cart-detail">
              <h2 className="add-cart-name">{quote.perfume.name}</h2>
              {quote.perfume.chords?.length > 0 && (
                <div className="add-cart-chords">
                  {quote.perfume.chords.map((chord) => (
                    <span key={chord} className="add-cart-chord">
                      {chord}
                    </span>
                  ))}
                </div>
              )}
              <Stars value={quote.perfume.stars} />
              <div className="add-cart-price-row">
                <p className="add-cart-total">
                  {formatMoney(Number(quote.total) * Math.max(1, Number(quantity) || 1), i18n.language)}
                  {pricing && <Spinner animation="border" size="sm" className="ms-2" />}
                </p>
                <Form.Group className="add-cart-quantity">
                  <Form.Label htmlFor="cart-quantity">{t("cart.quantity")}</Form.Label>
                  <Form.Control
                    id="cart-quantity"
                    type="number"
                    min={1}
                    step={1}
                    value={quantity}
                    onChange={(event) => setQuantity(event.target.value)}
                    disabled={saving || pricing}
                  />
                </Form.Group>
              </div>
              <div className="add-cart-options">
                {quote.perfume_option && (
                  <OptionCard
                    selected={quote.selected_container == null}
                    image={quote.perfume_option.image_url}
                    name={quote.perfume_option.name}
                    content={quote.perfume_option.content}
                    stockLabel={t("cart.inStock")}
                    disabled={pricing || saving}
                    onSelect={() => selectContainer(null)}
                  />
                )}
                {quote.containers.map((container) => (
                  <OptionCard
                    key={container.id}
                    selected={quote.selected_container === container.id}
                    image={container.image_url}
                    name={container.name}
                    content={container.content}
                    stockLabel={t("cart.inStock")}
                    disabled={pricing || saving}
                    onSelect={() => selectContainer(container.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={saving}>
          {t("admin.cancel")}
        </Button>
        <Button
          variant="dark"
          onClick={handleConfirm}
          disabled={saving || pricing || loading || !quote}
        >
          {t("home.addToCart")}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
