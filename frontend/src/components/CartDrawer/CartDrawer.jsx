import { Button, ListGroup, Offcanvas } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useCart } from "../../hooks/useCart";

export default function CartDrawer() {
  const { t } = useTranslation();
  const { items, open, setOpen, removeItem, checkout, total } = useCart();
  const navigate = useNavigate();

  async function handleCheckout() {
    await checkout();
    navigate("/pedidos");
  }

  return (
    <Offcanvas show={open} onHide={() => setOpen(false)} placement="end">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>{t("cart.title")}</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body className="d-flex flex-column">
        {items.length === 0 ? (
          <p className="text-body-secondary">{t("cart.empty")}</p>
        ) : (
          <>
            <ListGroup variant="flush" className="mb-3">
              {items.map((item) => (
                <ListGroup.Item key={item.id} className="px-0">
                  <div className="d-flex justify-content-between gap-3">
                    <div>
                      <strong>{item.perfume_name}</strong>
                      <div className="small text-body-secondary">
                        {item.brand} · x{item.quantity}
                      </div>
                    </div>
                    <div className="text-end">
                      <div>${(Number(item.price) * item.quantity).toFixed(2)}</div>
                      <Button variant="link" size="sm" className="p-0" onClick={() => removeItem(item.id)}>
                        {t("common.delete")}
                      </Button>
                    </div>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
            <div className="mt-auto">
              <p className="fw-semibold">
                {t("cart.total")}: ${total.toFixed(2)}
              </p>
              <Button variant="dark" className="w-100" onClick={handleCheckout}>
                {t("cart.checkout")}
              </Button>
            </div>
          </>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
