import { request } from "./apiClient";

export async function getAnalytics() {
  return await request("/analytics");
}

export async function getAuditLogs() {
  return await request("/audit-logs");
}
