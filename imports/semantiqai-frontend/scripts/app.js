async function apiGet(url, founderKey = "") {
  const headers = {};
  if (founderKey) headers["X-Founder-Key"] = founderKey;
  const res = await fetch(url, { headers });
  return await res.json();
}

async function apiPost(url, payload = {}, founderKey = "") {
  const headers = { "Content-Type": "application/json" };
  if (founderKey) headers["X-Founder-Key"] = founderKey;

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  });

  return await res.json();
}

function byId(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  const el = byId(id);
  if (el) el.textContent = value;
}

function pretty(data) {
  return JSON.stringify(data, null, 2);
}

function showView(viewName) {
  document.querySelectorAll("[data-view]").forEach(el => {
    el.classList.toggle("hidden", el.dataset.view !== viewName);
  });

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.target === viewName);
  });
}

async function refreshHealth() {
  try {
    const data = await apiGet("/health");
    setText("metric-health", data.status || "unknown");
    setText("hero-status", `System status: ${data.status || "unknown"}`);
  } catch (e) {
    setText("metric-health", "offline");
    setText("hero-status", "System status: unavailable");
  }
}

async function refreshAgents() {
  try {
    const data = await apiGet("/ai/agents");
    setText("metric-agents", (data.agents || []).length);
    const list = byId("agents-list");
    list.innerHTML = "";
    (data.agents || []).forEach(agent => {
      const div = document.createElement("div");
      div.className = "list-item";
      div.textContent = agent;
      list.appendChild(div);
    });
  } catch (e) {
    setText("metric-agents", "0");
  }
}

async function refreshFactoryRuns() {
  try {
    const data = await apiGet("/factory/runs");
    setText("metric-factory", (data.items || []).length);
    const list = byId("factory-runs");
    list.innerHTML = "";
    (data.items || []).slice(0, 8).forEach(item => {
      const div = document.createElement("div");
      div.className = "list-item";
      div.innerHTML = `<strong>${item.title || "Untitled"}</strong><div class="small">${item.content_type || ""}</div>`;
      list.appendChild(div);
    });
  } catch (e) {
    setText("metric-factory", "0");
  }
}

async function refreshEducationRuns() {
  try {
    const data = await apiGet("/education/runs");
    setText("metric-education", (data.items || []).length);
    const list = byId("education-runs");
    list.innerHTML = "";
    (data.items || []).slice(0, 8).forEach(item => {
      const div = document.createElement("div");
      div.className = "list-item";
      div.innerHTML = `<strong>${item.title || "Untitled"}</strong><div class="small">${item.run_type || ""}</div>`;
      list.appendChild(div);
    });
  } catch (e) {
    setText("metric-education", "0");
  }
}

async function refreshFounderStatus() {
  try {
    const key = byId("founder-key").value.trim();
    const data = await apiGet("/founder/status", key);
    setText("metric-founder", data.founder_mode ? "enabled" : "locked");
  } catch (e) {
    setText("metric-founder", "locked");
  }
}

async function runPrompt() {
  const prompt = byId("prompt-input").value.trim();
  const agent = byId("agent-select").value;
  const output = byId("prompt-output");

  if (!prompt) {
    output.textContent = "Enter a prompt first.";
    return;
  }

  output.textContent = "Running...";
  try {
    const payload = { prompt, agent: agent || null };
    const data = await apiPost("/ai/run", payload);
    output.textContent = pretty(data);
  } catch (e) {
    output.textContent = "Failed to run prompt.";
  }
}

async function runFactoryBundle() {
  const topic = byId("factory-topic").value.trim();
  const output = byId("factory-output");

  if (!topic) {
    output.textContent = "Enter a topic first.";
    return;
  }

  output.textContent = "Generating full bundle...";
  try {
    const data = await apiPost("/factory/full-bundle", { topic });
    output.textContent = pretty(data);
    refreshFactoryRuns();
  } catch (e) {
    output.textContent = "Factory generation failed.";
  }
}

async function runEducationPack() {
  const subject = byId("edu-subject").value.trim();
  const level = byId("edu-level").value.trim();
  const topic = byId("edu-topic").value.trim();
  const output = byId("education-output");

  if (!subject || !level || !topic) {
    output.textContent = "Subject, level, and topic are required.";
    return;
  }

  output.textContent = "Generating subject pack...";
  try {
    const data = await apiPost("/education/subject-pack", { subject, level, topic });
    output.textContent = pretty(data);
    refreshEducationRuns();
  } catch (e) {
    output.textContent = "Education generation failed.";
  }
}

async function runCognitiveDrill() {
  const focus_area = byId("cog-focus").value.trim();
  const difficulty = byId("cog-difficulty").value.trim();
  const output = byId("cognitive-output");

  if (!focus_area || !difficulty) {
    output.textContent = "Focus area and difficulty are required.";
    return;
  }

  output.textContent = "Generating drill...";
  try {
    const data = await apiPost("/cognitive/drill", { focus_area, difficulty });
    output.textContent = pretty(data);
  } catch (e) {
    output.textContent = "Cognitive drill generation failed.";
  }
}

async function runSimulation() {
  const name = byId("sim-name").value.trim();
  const domain = byId("sim-domain").value.trim();
  const objective = byId("sim-objective").value.trim();
  const constraintsRaw = byId("sim-constraints").value.trim();
  const output = byId("simulation-output");

  if (!name || !domain || !objective) {
    output.textContent = "Name, domain, and objective are required.";
    return;
  }

  const constraints = constraintsRaw
    ? constraintsRaw.split("\n").map(x => x.trim()).filter(Boolean)
    : [];

  output.textContent = "Running simulation...";
  try {
    const data = await apiPost("/simulation/run", { name, domain, objective, constraints });
    output.textContent = pretty(data);
  } catch (e) {
    output.textContent = "Simulation failed.";
  }
}

async function runGrowthPlan() {
  const target = byId("growth-target").value.trim();
  const platform = byId("growth-platform").value.trim();
  const cadence = byId("growth-cadence").value.trim();
  const output = byId("growth-output");

  if (!target || !platform || !cadence) {
    output.textContent = "Target, platform, and cadence are required.";
    return;
  }

  output.textContent = "Building growth plan...";
  try {
    const data = await apiPost("/growth/plan", { target, platform, cadence });
    output.textContent = pretty(data);
  } catch (e) {
    output.textContent = "Growth plan failed.";
  }
}

async function loadFounderDashboard() {
  const key = byId("founder-key").value.trim();
  const output = byId("founder-output");

  if (!key) {
    output.textContent = "Enter founder key first.";
    return;
  }

  output.textContent = "Loading founder dashboard...";
  try {
    const data = await apiGet("/founder/dashboard", key);
    output.textContent = pretty(data);
    refreshFounderStatus();
  } catch (e) {
    output.textContent = "Founder dashboard request failed.";
  }
}

async function generateFounderReport() {
  const key = byId("founder-key").value.trim();
  const output = byId("founder-output");

  if (!key) {
    output.textContent = "Enter founder key first.";
    return;
  }

  output.textContent = "Generating founder report...";
  try {
    const data = await apiPost("/founder/report", {}, key);
    output.textContent = pretty(data);
  } catch (e) {
    output.textContent = "Founder report failed.";
  }
}

function bindNav() {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => showView(btn.dataset.target));
  });
}

function bindActions() {
  byId("run-prompt-btn").addEventListener("click", runPrompt);
  byId("run-factory-btn").addEventListener("click", runFactoryBundle);
  byId("run-education-btn").addEventListener("click", runEducationPack);
  byId("run-cognitive-btn").addEventListener("click", runCognitiveDrill);
  byId("run-simulation-btn").addEventListener("click", runSimulation);
  byId("run-growth-btn").addEventListener("click", runGrowthPlan);
  byId("load-founder-btn").addEventListener("click", loadFounderDashboard);
  byId("report-founder-btn").addEventListener("click", generateFounderReport);
  byId("refresh-overview-btn").addEventListener("click", async () => {
    await refreshHealth();
    await refreshAgents();
    await refreshFactoryRuns();
    await refreshEducationRuns();
    await refreshFounderStatus();
  });
}

async function boot() {
  bindNav();
  bindActions();
  showView("overview");
  await refreshHealth();
  await refreshAgents();
  await refreshFactoryRuns();
  await refreshEducationRuns();
  await refreshFounderStatus();
}

window.addEventListener("DOMContentLoaded", boot);
