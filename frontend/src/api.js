const isLocalhost =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

export const API_BASE =
  window.__ZERENTHIS_API_BASE__ ||
  (isLocalhost
    ? "http://127.0.0.1:8000"
    : "https://semantiqai-backend-production-bcab.up.railway.app");

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
  return res.json();
}