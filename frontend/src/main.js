import { postSystemRun, API_BASE } from "./api.js";

const root = document.getElementById("app");

async function boot() {
  root.innerHTML = `
    <div style="background:#05070d;color:white;min-height:100vh;font-family:Arial,sans-serif;padding:32px;">
      <h1 style="margin-top:0;">Zerenthis Founder</h1>
      <p>API Base: <code>${API_BASE}</code></p>
      <button id="runBtn" style="padding:12px 18px;border:none;border-radius:10px;background:#00e5ff;color:black;font-weight:bold;cursor:pointer;">
        Run Core Test
      </button>
      <pre id="out" style="margin-top:20px;padding:16px;background:#111;border-radius:12px;white-space:pre-wrap;"></pre>
    </div>
  `;

  document.getElementById("runBtn").onclick = async () => {
    const out = document.getElementById("out");
    out.textContent = "Running...";
    try {
      const data = await postSystemRun("core_test", { hello: "world" });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      out.textContent = String(e);
    }
  };
}

boot();