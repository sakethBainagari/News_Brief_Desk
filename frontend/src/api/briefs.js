import { request } from "./apiClient";

export async function getBrief(id) {
  return await request(`/briefs/${id}`);
}

export async function updateBrief(id, headline, summary) {
  return await request(`/briefs/${id}`, {
    method: "PUT",
    body: JSON.stringify({ headline, summary })
  });
}

export async function submitBrief(id) {
  return await request(`/briefs/${id}/submit`, { method: "POST" });
}

export async function publishBrief(id) {
  return await request(`/briefs/${id}/publish`, { method: "POST" });
}
