import api from "./api";

export async function listPerfumeReviews(perfumeId) {
  const { data } = await api.get(`/perfumes/${perfumeId}/reviews/`);
  return data;
}

export async function createPerfumeReview(perfumeId, body) {
  const { data } = await api.post(`/perfumes/${perfumeId}/reviews/`, { body });
  return data;
}

export async function getCommunity(perfumeId) {
  const { data } = await api.get(`/perfumes/${perfumeId}/community/`);
  return data;
}

export async function setRating(perfumeId, sentiment) {
  const { data } = await api.post(`/perfumes/${perfumeId}/rating/`, { sentiment });
  return data;
}

export async function setOccasion(perfumeId, occasion, selected) {
  const { data } = await api.post(`/perfumes/${perfumeId}/occasions/`, { occasion, selected });
  return data;
}

export async function listMyReviews() {
  const { data } = await api.get("/reviews/");
  return data;
}

export async function deleteReview(id) {
  await api.delete(`/reviews/${id}/`);
}
