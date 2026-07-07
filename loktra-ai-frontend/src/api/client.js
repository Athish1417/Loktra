import axios from "axios";

// Empty base URL -> relative /api/... paths -> handled by the Vite dev proxy.
// Set VITE_API_BASE_URL for production (absolute backend URL).
const baseURL = import.meta.env.VITE_API_BASE_URL || "";

const client = axios.create({ baseURL });

// Attach the JWT on every request if present.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("loktra_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear the session so the app bounces back to login.
client.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("loktra_token");
      localStorage.removeItem("loktra_user");
    }
    return Promise.reject(error);
  }
);

// Normalise backend error detail (string, {message,reason}, or validation array)
// into a single readable string for toasts / inline errors.
export function errorMessage(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (!detail) return error?.message || fallback;
  if (typeof detail === "string") return detail;
  if (detail.message) {
    return detail.reason ? `${detail.message} (${detail.reason})` : detail.message;
  }
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg).filter(Boolean).join("; ") || fallback;
  }
  return fallback;
}

export default client;
