import api from "./api";

export async function getPoints() {
  const { data } = await api.get("/points/");
  return data;
}

export async function redeemReward(rewardId) {
  const { data } = await api.post("/points/redeem/", { reward: rewardId });
  return data;
}
