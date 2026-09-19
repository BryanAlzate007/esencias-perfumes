import axios from "axios";
import { getCSRFToken } from "../lib/csrf";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const csrf = getCSRFToken();
  if (csrf) {
    config.headers["X-CSRFToken"] = csrf;
  }
  return config;
});

export default api;
