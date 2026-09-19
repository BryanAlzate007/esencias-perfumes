import { getCSRFToken } from "./csrf";

const BASE_URL = "/_allauth/browser/v1";

function emitAuthChange(message) {
  document.dispatchEvent(new CustomEvent("allauth.auth.change", { detail: message }));
}

export function allauthErrors(message) {
  if (!message?.errors?.length) {
    return message?.detail || "";
  }
  return message.errors.map((error) => error.message).join(" ");
}

export async function allauthRequest(method, path, data, extraHeaders = {}) {
  const headers = {
    Accept: "application/json",
    "X-CSRFToken": getCSRFToken(),
    ...extraHeaders,
  };
  const options = {
    method,
    headers,
    credentials: "include",
  };

  if (typeof data !== "undefined") {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${BASE_URL}${path}`, options);
  const message = await response.json();

  if ([401, 410].includes(message.status) || (message.status === 200 && message.meta?.is_authenticated)) {
    emitAuthChange(message);
  }

  return message;
}

export function getAuth() {
  return allauthRequest("GET", "/auth/session");
}

export function login(data) {
  return allauthRequest("POST", "/auth/login", data);
}

export function signUp(data) {
  return allauthRequest("POST", "/auth/signup", data);
}

export function logout() {
  return allauthRequest("DELETE", "/auth/session");
}

export function requestPasswordReset(email) {
  return allauthRequest("POST", "/auth/password/request", { email });
}

export function getPasswordReset(key) {
  return allauthRequest("GET", "/auth/password/reset", undefined, {
    "X-Password-Reset-Key": key,
  });
}

export function resetPassword(data) {
  return allauthRequest("POST", "/auth/password/reset", data);
}

export function changePassword(data) {
  return allauthRequest("POST", "/account/password/change", data);
}
