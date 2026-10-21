import api from "./api";

export async function sendContact(payload) {
  const { data } = await api.post("/contact/", payload);
  return data;
}
