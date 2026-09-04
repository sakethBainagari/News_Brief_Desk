import { request } from "./apiClient";

export async function getRawItems(page = 1, limit = 20, category = "", source = "", search = "") {
  const params = new URLSearchParams({ page, limit });
  if (category) params.append("category", category);
  if (source) params.append("source", source);
  if (search) params.append("search", search);

  return await request(`/raw-items?${params.toString()}`);
}

export async function getRawItemDetail(id) {
  return await request(`/raw-items/${id}`);
}

export async function getRawItemsStats() {
  return await request("/stats/raw-items");
}
