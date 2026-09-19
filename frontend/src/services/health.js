import api from "./api";

export async function getHealth() {
  const { data } = await api.get("/health/");
  return data;
}
