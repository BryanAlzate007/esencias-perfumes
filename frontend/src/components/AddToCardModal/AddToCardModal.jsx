import { useEffect, useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useCart } from "../../hooks/useCart";
import { mediaUrl } from "../../lib/media";
import { previewQuote } from "../../services/orders";
import { formatMoney } from "../../lib/money";
import "./AddToCardModal.css";

export default function AddToCartModal({ perfumeId, show, onHide, onAdded }) {
  const { t, i18n } = useTranslation();
  const { saveQuote } = useCart();
  const [quote, setQuote] = useState(null);
  const [grams, setGrams] = useState(100);
  const [loading, setLoading] = useState(false);
  const [pricing, setPricing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const quoteRef = useRef(null);
  const gramsRef = useRef(grams);
  const timer = useRef(null);
  const requestSeq = useRef(0);

  quoteRef.current = quote;
  gramsRef.current = grams;

  useEffect(() => {
    if (!show || !perfumeId) {
      return undefined;
    }
    let active = true;
    setLoading(true);
    setError("");
    setQuote(null);
    previewQuote({ perfume: perfumeId })
      .then((data) => {
        if (!active) {
          return;
        }
        setQuote(data);
        setGrams(data.grams);
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
      clearTimeout(timer.current);
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
      setGrams(data.grams);
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
    clearTimeout(timer.current);
    const base = current.base_grams;
    const nextGrams = Number(gramsRef.current);
    applyQuote({
      container: containerId,
      grams: Number.isFinite(nextGrams) && nextGrams >= base ? nextGrams : base,
    });
  }

  function changeGrams(nextValue) {
    setGrams(nextValue);
    const current = quoteRef.current;
    const parsed = Number(nextValue);
    if (!current?.selected_container || !Number.isFinite(parsed) || parsed < 1) {
      return;
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      applyQuote({
        container: current.selected_container,
        grams: parsed,
      });
    }, 400);
  }

  async function handleConfirm() {
    if (!quote) {
      return;
    }
    setSaving(true);
    setError("");
    clearTimeout(timer.current);
    try {
      await saveQuote(quote);
      onAdded?.();
      onHide();
    } catch {
      setError(t("cart.quoteError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal show={show} onHide={onHide} centered className="add-cart-modal">
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
          <>
            {mediaUrl(quote.perfume.image_url) && (
              <img className="add-cart-lotion" src={mediaUrl(quote.perfume.image_url)} alt={quote.perfume.name} />
            )}
            <div className="add-cart-price-row">
              <p className="add-cart-total">
                {formatMoney(quote.total, i18n.language)}
                {pricing && <Spinner animation="border" size="sm" className="ms-2" />}
              </p>
              {quote.selected_container != null && (
                <Form.Group className="add-cart-grams">
                  <Form.Label htmlFor="cart-grams">{t("cart.grams")}</Form.Label>
                  <Form.Control
                    id="cart-grams"
                    type="number"
                    min={quote.base_grams}
                    step={1}
                    value={grams}
                    onChange={(event) => changeGrams(event.target.value)}
                    disabled={saving}
                  />
                </Form.Group>
              )}
            </div>
            <div className="add-cart-options">
              {quote.containers.map((container) => {
                const selected = quote.selected_container === container.id;
                return (
                  <label key={container.id} className={selected ? "add-cart-option is-selected" : "add-cart-option"}>
                    {mediaUrl(container.image_url) && <img src={mediaUrl(container.image_url)} alt="" />}
                    <span className="add-cart-option-copy">
                      <input
                        type="radio"
                        name="container"
                        checked={selected}
                        onChange={() => selectContainer(container.id)}
                        disabled={pricing || saving}
                      />
                      <span>{container.name}</span>
                    </span>
                  </label>
                );
              })}
            </div>
          </>
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
