import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("token");
    }
    return Promise.reject(err);
  }
);

// --- Auth ---
export function login(email, password) {
  return api.post("/auth/login", { email, password });
}

export function signup(email, password) {
  return api.post("/auth/signup", { email, password });
}

// --- Scans ---
export function submitScan(url) {
  return api.post("/scan", { url });
}

export function getHistory() {
  return api.get("/history");
}

export function getReport(id) {
  return api.get(`/reports/${id}`);
}

export function getReportDownloadUrl(id) {
  return `${BASE_URL}/reports/${id}/download`;
}
