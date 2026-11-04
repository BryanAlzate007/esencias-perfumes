import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import { Link } from "react-router-dom";
import { sendChatMessage } from "../../services/chat";
import "./ChatIA.css";

const STORAGE_KEY = "esencias-advisor-chat";

let messageSeq = 0;

function nextMessageId() {
  messageSeq += 1;
  return `msg-${messageSeq}`;
}

function chatLanguage() {
  const code = (i18n.resolvedLanguage || i18n.language || "es").toLowerCase();
  return code.startsWith("en") ? "en" : "es";
}

function readSession() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const data = JSON.parse(raw);
    if (!data || typeof data !== "object") {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}

export default function ChatIA() {
  const { t } = useTranslation();
  const [session] = useState(readSession);
  const [language] = useState(() => session?.language || chatLanguage());
  const fixed = i18n.getFixedT(language);
  const [greetingIndex] = useState(() => {
    const options = fixed("chat.greetings", { returnObjects: true });
    const list = Array.isArray(options) ? options : [];
    if (session?.advisor) {
      const found = list.findIndex((item) => item.advisor === session.advisor);
      if (found >= 0) {
        return found;
      }
    }
    return list.length ? Math.floor(Math.random() * list.length) : 0;
  });
  const [messages, setMessages] = useState(() => (Array.isArray(session?.messages) ? session.messages : []));
  const [chatId, setChatId] = useState(session?.chatId || "");
  const [phase, setPhase] = useState(session?.phase || "question");
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const threadRef = useRef(null);
  const greetings = fixed("chat.greetings", { returnObjects: true });
  const greeting = Array.isArray(greetings) ? greetings[greetingIndex] : null;
  const advisorName = greeting?.advisor || "Sofía";
  const welcome = fixed("chat.welcome", {
    name: advisorName,
    role: greeting?.role || "asesora",
  });
  const thread = [{ id: "welcome", role: "assistant", text: welcome }, ...messages];

  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
        chatId,
        advisor: advisorName,
        language,
        phase,
        messages,
      }));
    } catch {
      // The conversation still works if the browser blocks storage.
    }
  }, [advisorName, chatId, language, messages, phase]);

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
      const data = await sendChatMessage({
        message: text,
        chatId,
        advisor: advisorName,
        language,
      });
      if (data?.chat_id) {
        setChatId(data.chat_id);
      }
      if (data?.phase) {
        setPhase(data.phase);
      }
      const reply = typeof data?.response === "string" ? data.response.trim() : "";
      setMessages((current) => [
        ...current,
        { id: nextMessageId(), role: "assistant", text: reply || t("chat.error") },
      ]);
    } catch (error) {
      if (error?.response?.status === 404) {
        setChatId("");
        setPhase("question");
      }
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

  const placeholder = phase === "email" ? fixed("chat.emailPlaceholder") : fixed("chat.placeholder");

  return (
    <section className="chat-ia" aria-label={t("chat.title")}>
      <header className="chat-ia-header">
        <Link className="chat-ia-back" to="/perfumes">
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
          {placeholder}
        </label>
        <textarea
          id="chat-ia-input"
          rows={1}
          value={draft}
          placeholder={placeholder}
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
