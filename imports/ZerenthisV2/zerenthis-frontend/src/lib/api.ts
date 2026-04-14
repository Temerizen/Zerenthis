export const API_BASE = "http://127.0.0.1:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      cache: "no-store",
    });

    const text = await res.text();

    let parsed: any = null;
    try {
      parsed = text ? JSON.parse(text) : {};
    } catch {
      parsed = { raw: text };
    }

    if (!res.ok) {
      return {
        error: true,
        status: res.status,
        path,
        ...parsed,
      };
    }

    return parsed;
  } catch (error: any) {
    return {
      error: true,
      path,
      message: error?.message || "Failed to fetch",
    };
  }
}

// SYSTEM
export const getHealth = () => apiFetch("/health");
export const getPhaseVerify = () => apiFetch("/api/phase/verify");

// TARGETS
export const getTargets = () =>
  apiFetch("/api/targets/rank", { method: "POST" });

// AUTOPILOT
export const runAutopilot = () =>
  apiFetch("/api/autopilot/run", { method: "POST" });

// POSTING
export const runPostingPlan = () =>
  apiFetch("/api/posting/plan", { method: "POST" });

export const runPostingPrepare = () =>
  apiFetch("/api/posting/prepare", { method: "POST" });

export const runPostingExecute = () =>
  apiFetch("/api/posting/execute", { method: "POST" });

export const getPostingResult = () =>
  apiFetch("/api/posting/result", { method: "POST" });

// REALITY
export const runRealityLoop = () =>
  apiFetch("/api/reality/loop", { method: "POST" });

export const runRealityAutoLoop = () =>
  apiFetch("/api/reality/auto-loop", { method: "POST" });

export const runRealityExport = () =>
  apiFetch("/api/reality/export", { method: "POST" });

// SCALE
export const runScale = () =>
  apiFetch("/api/scale/run", { method: "POST" });

// TRAFFIC
export const runTrafficReal = () =>
  apiFetch("/api/traffic/real", { method: "POST" });

export const runTrafficBridge = () =>
  apiFetch("/api/traffic/bridge", { method: "POST" });
