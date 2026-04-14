const root = document.getElementById("app");

root.innerHTML = `
<h1>Zerenthis GOD MODE</h1>
<textarea id="goal" style="width:100%;height:120px;"></textarea>
<button onclick="run()">RUN AUTOPILOT</button>
<pre id="out"></pre>
`;

async function run(){
  const goal = document.getElementById("goal").value;
  const out = document.getElementById("out");
  out.textContent = "Running evolution cycle...";

  const res = await fetch("/api/autopilot", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({goal})
  });

  const data = await res.json();
  out.textContent = JSON.stringify(data,null,2);
}