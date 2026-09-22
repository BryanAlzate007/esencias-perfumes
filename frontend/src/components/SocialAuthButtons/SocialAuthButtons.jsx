import { getCSRFToken } from "../../lib/csrf";
import "./SocialAuthButtons.css";

const PROVIDERS = [
  { id: "google", label: "Google" },
  { id: "facebook", label: "Facebook" },
  { id: "apple", label: "Apple" },
];

export default function SocialAuthButtons({ process = "login" }) {
  function startProvider(provider) {
    sessionStorage.setItem("esencias-auth-next", window.location.pathname || "/");
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/_allauth/browser/v1/auth/provider/redirect";
    const fields = {
      csrfmiddlewaretoken: getCSRFToken(),
      provider,
      callback_url: `${window.location.origin}/auth/callback`,
      process,
    };
    Object.entries(fields).forEach(([name, value]) => {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      input.value = value;
      form.appendChild(input);
    });
    document.body.appendChild(form);
    form.submit();
  }

  return (
    <div className="social-auth">
      {PROVIDERS.map((provider) => (
        <button
          key={provider.id}
          type="button"
          className={`social-auth-button social-auth-button-${provider.id}`}
          onClick={() => startProvider(provider.id)}
        >
          <SocialIcon provider={provider.id} />
          <span>{provider.label}</span>
        </button>
      ))}
    </div>
  );
}

function SocialIcon({ provider }) {
  if (provider === "google") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path fill="#EA4335" d="M12 10.2v3.6h5.1c-.2 1.2-1.5 3.6-5.1 3.6-3.1 0-5.6-2.6-5.6-5.7S8.9 6 12 6c1.8 0 3 .7 3.7 1.4l2.5-2.4C16.7 3.6 14.5 2.6 12 2.6 6.9 2.6 2.8 6.7 2.8 11.7S6.9 20.8 12 20.8c5.3 0 8.8-3.7 8.8-9 0-.6-.1-1-.2-1.6H12z" />
      </svg>
    );
  }
  if (provider === "facebook") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M14.5 8.5V6.8c0-.7.5-1 1.2-1h1.5V3h-2.6C11.8 3 10.5 4.6 10.5 7v1.5H8.2V11h2.3v10h3.9V11h2.5l.4-2.5h-2.8z" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M16.7 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.2-2.8.8-3.5.8s-1.8-.8-3-.8c-1.5 0-3 .9-3.7 2.3-1.6 2.8-.4 6.9 1.1 9.2.8 1.1 1.7 2.3 2.9 2.3 1.1 0 1.6-.8 3-.8s1.8.8 3 .8 2-1.2 2.8-2.3c.9-1.3 1.3-2.5 1.3-2.6-.1 0-2.5-1-2.5-3.4zM14.6 5.8c.6-.8 1.1-1.8.9-2.9-1 .1-2.1.7-2.7 1.5-.6.7-1.1 1.8-.9 2.8 1.1.1 2.1-.6 2.7-1.4z" />
    </svg>
  );
}
