import api from "./api";

export async function sendChatMessage({ message, chatId, advisor, language }) {
  const payload = { message, advisor, language };
  if (chatId) {
    payload.chat_id = chatId;
  }
  const { data } = await api.post("/chat/", payload);
  return data;
}
