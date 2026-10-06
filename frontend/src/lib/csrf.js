let csrfToken = "";

export function setCSRFToken(token) {
  if (token) {
    csrfToken = token;
  }
}

export function getCSRFToken() {
  if (csrfToken) {
    return csrfToken;
  }
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}
