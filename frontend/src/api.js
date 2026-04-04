export const API_BASE =
  window.__ZERENTHIS_API_BASE__ ||
  "https://semantiqai-backend-production-bcab.up.railway.app";

async function parseResponse(res) {
  const text = await res.text();
  try { return JSON.parse(text); } catch { return text; }
}

export async function postSystemRun(engine, payload = {}) {
  const res = await fetch(`${API_BASE}/api/system/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ engine, payload })
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`System run failed: ${res.status} ${text}`);
  }
  return parseResponse(res);
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health failed: ${res.status}`);
  return parseResponse(res);
}

export async function getWinners() {
  const res = await fetch(`${API_BASE}/api/winners`, { method: "POST" });
  if (!res.ok) throw new Error(`Winners failed: ${res.status}`);
  return parseResponse(res);
}