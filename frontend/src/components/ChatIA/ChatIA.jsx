import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import { Link } from "react-router-dom";
import { sendChatMessage } from "../../services/chat";
import "./ChatIA.css";

let messageSeq = 0;

function nextMessageId() {
  messageSeq += 1;
  return `msg-${messageSeq}`;
}

export default function ChatIA() {
  const { t } = useTranslation();
  const [greetingIndex] = useState(() => {
    const options = i18n.t("chat.greetings", { returnObjects: true });
    const count = Array.isArray(options) ? options.length : 1;
    return Math.floor(Math.random() * count);
  });
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const threadRef = useRef(null);
  const greetings = t("chat.greetings", { returnObjects: true });
  const greeting = Array.isArray(greetings) ? greetings[greetingIndex] : null;
  const advisorName = greeting?.advisor || "";
  const thread = [{ id: "welcome", role: "assistant", text: greeting?.welcome || "" }, ...messages];

  useEffect(() => {
    const node = threadRef.current;
    if (!node) {
      return;
    }
    node.scrollTop = node.scrollHeight;
  }, [thread.length, sending]);

  async function handleSubmit(event) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || sending) {
      return;
    }
    setMessages((current) => [...current, { id: nextMessageId(), role: "user", text }]);
    setDraft("");
    setSending(true);
    try {
      const data = await sendChatMessage(text);
      const reply = typeof data?.response === "string" ? data.response.trim() : "";
      setMessages((current) => [
        ...current,
        { id: nextMessageId(), role: "assistant", text: reply || t("chat.error") },
      ]);
    } catch (error) {
      const apiError = error?.response?.data?.error;
      const fieldError = error?.response?.data?.message;
      const detail = typeof apiError === "string"
        ? apiError
        : Array.isArray(fieldError)
          ? fieldError[0]
          : "";
      setMessages((current) => [
        ...current,
        { id: nextMessageId(), role: "assistant", text: detail || t("chat.error") },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="chat-ia" aria-label={t("chat.title")}>
      <header className="chat-ia-header">
        <Link className="chat-ia-back" to="/">
          {t("chat.back")}
        </Link>
        <div>
          <p className="chat-ia-kicker">{t("chat.kicker")}</p>
          <h1 className="chat-ia-title">{t("chat.title")}</h1>
        </div>
      </header>

      <div className="chat-ia-thread" ref={threadRef} role="log" aria-live="polite">
        <div className="chat-ia-thread-inner">
          {thread.map((message) => (
            <article key={message.id} className={`chat-ia-bubble chat-ia-bubble-${message.role}`}>
              <span className="chat-ia-bubble-label">
                {message.role === "user" ? t("chat.you") : advisorName}
              </span>
              <p>{message.text}</p>
            </article>
          ))}
          {sending && (
            <article className="chat-ia-bubble chat-ia-bubble-assistant chat-ia-bubble-pending">
              <span className="chat-ia-bubble-label">{advisorName}</span>
              <p>{t("chat.thinking")}</p>
            </article>
          )}
        </div>
      </div>

      <form className="chat-ia-composer" onSubmit={handleSubmit}>
        <label className="visually-hidden" htmlFor="chat-ia-input">
          {t("chat.placeholder")}
        </label>
        <textarea
          id="chat-ia-input"
          rows={1}
          value={draft}
          placeholder={t("chat.placeholder")}
          disabled={sending}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <button type="submit" disabled={sending || !draft.trim()}>
          {t("chat.send")}
        </button>
      </form>
    </section>
  );
}
