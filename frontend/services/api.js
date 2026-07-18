/**
 * Single point of contact with the backend. Every component calls these
 * functions instead of using axios directly - this is what keeps the
 * frontend/backend contract in one place.
 */
import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_URL;

const api = axios.create({
  baseURL: BASE,
  timeout: 120000, // 2 minutes - handles Render cold start
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function sendMessage(sessionId, message) {
  const { data } = await api.post("/chat", {
    session_id: sessionId,
    message,
  });
  return data;
}

export async function getHistory(sessionId) {
  const { data } = await api.get(`/conversations/${sessionId}`);
  return data;
}

export async function listConversations() {
  const { data } = await api.get("/conversations");
  return data;
}

export async function register(email, password, name) {
  const { data } = await api.post("/auth/register", {
    email,
    password,
    name,
  });
  return data;
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export default api;
