let csrfToken = "";

export function setCSRFToken(token) {
  if (token) {
    csrfToken = token;
  }
}

export function getCSRFToken() {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
  if (match) {
    return decodeURIComponent(match[1]);
  }
  return csrfToken;
}
