import { API_BASE, postSystemRun, getHealth, getWinners } from "./api.js";

const root = document.getElementById("app");

function btn(label, id, bg = "#00e5ff", fg = "black") {
  return `<button id="${id}" style="padding:12px 18px;border:none;border-radius:12px;background:${bg};color:${fg};font-weight:700;cursor:pointer;">${label}</button>`;
}

function render() {
  root.innerHTML = `
    <div style="background:#05070d;color:white;min-height:100vh;font-family:Arial,sans-serif;padding:28px;box-sizing:border-box;">
      <h1 style="margin:0 0 12px 0;font-size:52px;">Zerenthis Founder</h1>
      <div style="opacity:.9;margin-bottom:18px;">API Base: <code>${API_BASE}</code></div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;max-width:1180px;margin-bottom:22px;">
        ${btn("Run Founder Engine", "founderBtn")}
        ${btn("Run Money Engine", "moneyBtn", "#22c55e", "black")}
        ${btn("Run Product Engine", "productBtn", "#f59e0b", "black")}
        ${btn("Run Builder", "builderBtn", "#06b6d4", "black")}
        ${btn("Run Watcher", "watcherBtn", "#ef4444", "white")}
        ${btn("Run Execution Layer", "execBtn", "#14b8a6", "black")}
        ${btn("System Health", "healthBtn", "#8b5cf6", "white")}
        ${btn("View Winners", "winnersBtn", "#334155", "white")}
      </div>

      <div style="padding:18px;background:#0d1117;border-radius:16px;border:1px solid #1f2937;max-width:1320px;">
        <div style="font-size:14px;opacity:.8;margin-bottom:10px;">Output</div>
        <pre id="out" style="margin:0;white-space:pre-wrap;word-break:break-word;font-size:14px;min-height:260px;"></pre>
      </div>
    </div>
  `;

  const out = document.getElementById("out");
  const show = (value) => {
    out.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  };

  document.getElementById("founderBtn").onclick = async () => {
    show("Running founder engine...");
    try { show(await postSystemRun("founder_engine", {})); } catch (e) { show(String(e)); }
  };

  document.getElementById("moneyBtn").onclick = async () => {
    show("Running money engine...");
    try { show(await postSystemRun("money_engine", {})); } catch (e) { show(String(e)); }
  };

  document.getElementById("productBtn").onclick = async () => {
    show("Running product engine...");
    try {
      show(await postSystemRun("product_engine", {
        topic: "AI Starter Product Pack",
        niche: "Content Monetization"
      }));
    } catch (e) { show(String(e)); }
  };

  document.getElementById("builderBtn").onclick = async () => {
    show("Running builder...");
    try { show(await postSystemRun("builder_engine", { limit: 8 })); } catch (e) { show(String(e)); }
  };

  document.getElementById("watcherBtn").onclick = async () => {
    show("Running watcher...");
    try { show(await postSystemRun("watcher_engine", {})); } catch (e) { show(String(e)); }
  };

  document.getElementById("execBtn").onclick = async () => {
    show("Running execution layer...");
    try { show(await postSystemRun("execution_engine", {})); } catch (e) { show(String(e)); }
  };

  document.getElementById("healthBtn").onclick = async () => {
    show("Checking system health...");
    try { show(await getHealth()); } catch (e) { show(String(e)); }
  };

  document.getElementById("winnersBtn").onclick = async () => {
    show("Loading winners...");
    try { show(await getWinners()); } catch (e) { show(String(e)); }
  };
}

render();