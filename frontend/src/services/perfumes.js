import api from "./api";

export async function listPerfumes() {
  const { data } = await api.get("/perfumes/");
  return data;
}

export async function getPerfume(id) {
  const { data } = await api.get(`/perfumes/${id}/`);
  return data;
}

export async function createPerfume(payload) {
  const { data } = await api.post("/perfumes/", payload);
  return data;
}

export async function updatePerfume(id, payload) {
  const { data } = await api.patch(`/perfumes/${id}/`, payload);
  return data;
}

export async function deletePerfume(id) {
  await api.delete(`/perfumes/${id}/`);
}
