import api from "./api";

export async function getCart() {
  const { data } = await api.get("/cart/");
  return data;
}

export async function addToCart(perfumeId, quantity = 1) {
  const { data } = await api.post("/cart/", { perfume: perfumeId, quantity });
  return data;
}

export async function updateCartItem(id, quantity) {
  const { data } = await api.patch(`/cart/${id}/`, { quantity });
  return data;
}

export async function removeCartItem(id) {
  await api.delete(`/cart/${id}/`);
}

export async function checkout() {
  const { data } = await api.post("/orders/checkout/");
  return data;
}

export async function listOrders() {
  const { data } = await api.get("/orders/");
  return data;
}

export async function updateOrder(id, payload) {
  const { data } = await api.patch(`/orders/${id}/`, payload);
  return data;
}

export async function listMyPerfumes() {
  const { data } = await api.get("/my-perfumes/");
  return data;
}
