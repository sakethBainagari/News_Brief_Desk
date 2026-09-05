const rawBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";
const API_BASE = rawBase.replace(/\/+$/, "");

export async function request(endpoint, options = {}) {
  const token = localStorage.getItem("news_desk_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const response = await fetch(`${API_BASE}${cleanEndpoint}`, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("news_desk_token");
      window.dispatchEvent(new Event("auth_unauthorized"));
    }
    const error = new Error(data.message || `HTTP ${response.status} Error`);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
