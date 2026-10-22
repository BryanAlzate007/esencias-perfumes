import api from "./api";

export async function getReferrals() {
  const { data } = await api.get("/referrals/");
  return data;
}

export async function claimReferral(code) {
  const { data } = await api.post("/referrals/claim/", { code });
  return data;
}
