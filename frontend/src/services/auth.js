import api from "./api";

export async function ensureCsrfCookie() {
  await api.get("/csrf/");
}

export async function getMe() {
  const { data } = await api.get("/me/");
  return data;
}

export async function updateMe(payload) {
  const { data } = await api.patch("/me/", payload);
  return data;
}

export async function listUsers() {
  const { data } = await api.get("/users/");
  return data;
}

export async function updateUser(id, payload) {
  const { data } = await api.patch(`/users/${id}/`, payload);
  return data;
}
