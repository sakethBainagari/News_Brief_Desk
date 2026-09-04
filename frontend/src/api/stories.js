import { request } from "./apiClient";

export async function getStories(page = 1, limit = 50) {
  return await request(`/stories?page=${page}&limit=${limit}`);
}

export async function getStoryDetail(id) {
  return await request(`/stories/${id}`);
}

export async function runClustering() {
  return await request("/stories/cluster", { method: "POST" });
}

export async function mergeStories(sourceStoryId, targetStoryId, reason = "") {
  return await request("/stories/merge", {
    method: "POST",
    body: JSON.stringify({
      source_story_id: sourceStoryId,
      target_story_id: targetStoryId,
      reason
    })
  });
}

export async function resetDemoData() {
  return await request("/demo/reset", { method: "POST" });
}

