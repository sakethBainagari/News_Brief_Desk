import { request } from "./apiClient";

export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
  if (data.access_token) {
    localStorage.setItem("news_desk_token", data.access_token);
  }
  return data;
}

export async function getMe() {
  return await request("/auth/me");
}

export function logout() {
  localStorage.removeItem("news_desk_token");
}
