/**
 * Single point of contact with the backend. Every component calls these
 * functions instead of using axios directly - this is what keeps the
 * frontend/backend contract in one place.
 */
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function sendMessage(sessionId, message) {
  const { data } = await api.post("/chat", { session_id: sessionId, message });
  return data; // { response, agents_used, trace }
}

export async function getHistory(sessionId) {
  const { data } = await api.get(`/conversations/${sessionId}`);
  return data; // { session_id, messages }
}

export async function register(email, password, name) {
  const { data } = await api.post("/auth/register", { email, password, name });
  return data; // { access_token }
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data; // { access_token }
}

export default api;
