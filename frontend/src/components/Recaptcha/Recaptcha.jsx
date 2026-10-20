import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";

const SCRIPT_ID = "recaptcha-enterprise";

function enterpriseApi() {
  return window.grecaptcha?.enterprise;
}

function loadRecaptcha(language) {
  if (enterpriseApi()?.ready) {
    return Promise.resolve(enterpriseApi());
  }
  return new Promise((resolve, reject) => {
    const finish = () => {
      if (enterpriseApi()?.ready) {
        resolve(enterpriseApi());
        return;
      }
      reject(new Error("captcha"));
    };
    const existing = document.getElementById(SCRIPT_ID);
    if (existing) {
      if (enterpriseApi()?.ready) {
        resolve(enterpriseApi());
        return;
      }
      existing.addEventListener("load", finish, { once: true });
      existing.addEventListener("error", () => reject(new Error("captcha")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = `https://www.google.com/recaptcha/enterprise.js?render=explicit&hl=${encodeURIComponent(language || "es")}`;
    script.async = true;
    script.onload = finish;
    script.onerror = () => reject(new Error("captcha"));
    document.head.appendChild(script);
  });
}

const Recaptcha = forwardRef(function Recaptcha({ siteKey, action = "SIGNUP", theme = "light", language = "es", onChange, onError }, ref) {
  const node = useRef(null);
  const widgetId = useRef(null);
  const onChangeRef = useRef(onChange);
  const onErrorRef = useRef(onError);
  onChangeRef.current = onChange;
  onErrorRef.current = onError;

  useImperativeHandle(ref, () => ({
    reset() {
      if (widgetId.current !== null && enterpriseApi()?.reset) {
        enterpriseApi().reset(widgetId.current);
      }
      onChangeRef.current("");
    },
  }));

  useEffect(() => {
    if (!siteKey || !node.current) {
      return undefined;
    }
    let cancelled = false;
    loadRecaptcha(language)
      .then((grecaptcha) => {
        grecaptcha.ready(() => {
          if (cancelled || !node.current || widgetId.current !== null) {
            return;
          }
          widgetId.current = grecaptcha.render(node.current, {
            sitekey: siteKey,
            action,
            theme: theme === "dark" ? "dark" : "light",
            callback: (token) => onChangeRef.current(token),
            "expired-callback": () => onChangeRef.current(""),
            "error-callback": () => onChangeRef.current(""),
          });
        });
      })
      .catch(() => {
        if (!cancelled) {
          onChangeRef.current("");
          onErrorRef.current?.();
        }
      });
    return () => {
      cancelled = true;
    };
  }, [siteKey, action, theme, language]);

  return <div ref={node} className="auth-captcha" />;
});

export default Recaptcha;
