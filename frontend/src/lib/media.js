export function mediaUrl(path) {
  if (!path) {
    return "";
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const apiUrl = import.meta.env.VITE_API_URL || "/api/v1";
  if (apiUrl.startsWith("http://") || apiUrl.startsWith("https://")) {
    return `${new URL(apiUrl).origin}${normalized}`;
  }
  return normalized;
}
