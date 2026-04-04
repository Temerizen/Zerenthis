const root = document.getElementById("app");

root.innerHTML = `
<h1>Zerenthis AI Control</h1>
<textarea id="msg" style="width:100%;height:120px;"></textarea>
<button onclick="send()">Execute</button>
<pre id="out"></pre>
`;

async function send(){
  const msg = document.getElementById("msg").value;
  const out = document.getElementById("out");
  out.textContent = "Thinking...";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({message: msg})
  });

  const data = await res.json();
  out.textContent = JSON.stringify(data,null,2);
}