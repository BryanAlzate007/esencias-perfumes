import api from "./api";

export async function startPayment(orderId) {
  const payload = orderId ? { order: orderId } : {};
  const { data } = await api.post("/payments/", payload);
  return data;
}

export async function syncPayment(transactionId) {
  const { data } = await api.post("/payments/sync/", { transaction_id: transactionId });
  return data;
}
