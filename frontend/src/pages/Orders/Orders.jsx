import { useEffect, useState } from "react";
import { Alert, Badge, Card, Form, ListGroup } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../hooks/useAuth";
import { listOrders, updateOrder } from "../../services/orders";

export default function Orders() {
  const { t, i18n } = useTranslation();
  const { isAdmin } = useAuth();
  const [orders, setOrders] = useState([]);

  async function load() {
    const data = await listOrders();
    setOrders(data.results || []);
  }

  useEffect(() => {
    load().catch(() => setOrders([]));
  }, []);

  async function handleStatus(id, status) {
    await updateOrder(id, { status });
    await load();
  }

  return (
    <>
      <h1 className="h2 mb-4">{t("orders.title")}</h1>
      {orders.length === 0 && <Alert variant="light">{t("orders.empty")}</Alert>}
      {orders.map((order) => (
        <Card key={order.id} className="mb-3">
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <div>
                <strong>#{order.id}</strong>
                {isAdmin && <span className="ms-2 text-body-secondary">{order.username}</span>}
                <div className="small text-body-secondary">
                  {new Intl.DateTimeFormat(i18n.language, { dateStyle: "medium" }).format(new Date(order.created_at))}
                </div>
              </div>
              {isAdmin ? (
                <Form.Select
                  value={order.status}
                  onChange={(event) => handleStatus(order.id, event.target.value)}
                  style={{ maxWidth: "12rem" }}
                >
                  <option value="pending">{t("orders.pending")}</option>
                  <option value="confirmed">{t("orders.confirmed")}</option>
                  <option value="cancelled">{t("orders.cancelled")}</option>
                </Form.Select>
              ) : (
                <Badge bg="secondary">{t(`orders.${order.status}`)}</Badge>
              )}
            </div>
            <ListGroup variant="flush">
              {order.items.map((item) => (
                <ListGroup.Item key={item.id} className="px-0">
                  {item.perfume_name} · x{item.quantity} · ${Number(item.subtotal).toFixed(2)}
                </ListGroup.Item>
              ))}
            </ListGroup>
            <p className="fw-semibold mt-3 mb-0">
              {t("cart.total")}: ${Number(order.total).toFixed(2)}
            </p>
          </Card.Body>
        </Card>
      ))}
    </>
  );
}
