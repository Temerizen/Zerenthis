"use client";

import { useMemo, useState } from "react";

type Mode = "product" | "shorts" | "youtube";

export default function Page() {
  const [mode, setMode] = useState<Mode>("product");
  const [apiBase, setApiBase] = useState("");
  const [topic, setTopic] = useState("");
  const [niche, setNiche] = useState("Make Money Online");
  const [tone, setTone] = useState("Premium");
  const [buyer, setBuyer] = useState("Beginners starting from zero");
  const [promise, setPromise] = useState("");
  const [bonus, setBonus] = useState("");
  const [notes, setNotes] = useState("");
  const [duration, setDuration] = useState(35);
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState("Waiting.");
  const [fileUrl, setFileUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const endpoint = useMemo(() => {
    if (mode === "product") return "/api/product-pack";
    if (mode === "shorts") return "/api/shorts-pack";
    return "/api/youtube-pack";
  }, [mode]);

  async function generate() {
    if (!apiBase.trim()) {
      setStatus("Enter backend URL.");
      return;
    }
    if (!topic.trim()) {
      setStatus("Enter topic.");
      return;
    }

    setLoading(true);
    setOutput("");
    setFileUrl("");
    setStatus("Submitting...");

    try {
      const res = await fetch(apiBase.replace(/\/$/, "") + endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          niche,
          tone,
          buyer,
          promise,
          bonus,
          notes,
          duration_seconds: duration,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Request failed");
      }

      if (data.job_id) {
        setStatus("Job queued...");
        await pollJob(data.job_id);
      } else {
        setOutput(JSON.stringify(data, null, 2));
        setStatus("Done.");
      }
    } catch (error: any) {
      setStatus(error?.message || "Failed.");
    } finally {
      setLoading(false);
    }
  }

  async function pollJob(jobId: string) {
    const base = apiBase.replace(/\/$/, "");

    return new Promise<void>((resolve) => {
      const timer = setInterval(async () => {
        try {
          const res = await fetch(`${base}/api/job/${jobId}`);
          const data = await res.json();

          setOutput(JSON.stringify(data, null, 2));

          if (data.status === "queued" || data.status === "running") {
            setStatus(`Job ${data.status}...`);
            return;
          }

          clearInterval(timer);

          if (data.status === "done") {
            setStatus("Done.");
            if (data.file_url) setFileUrl(base + data.file_url);
          } else {
            setStatus(data.error || "Job failed.");
          }

          resolve();
        } catch {
          clearInterval(timer);
          setStatus("Polling failed.");
          resolve();
        }
      }, 2000);
    });
  }

  return (
    <main className="page">
      <div className="shell">
        <div className="hero">
          <div className="eyebrow">Zerenthis Admin</div>
          <h1>Control products, shorts, and YouTube packs.</h1>
          <p>Use this panel to test your backend without touching the public site.</p>
        </div>

        <div className="grid">
          <section className="panel">
            <h2>Controls</h2>

            <label>Backend URL</label>
            <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />

            <div className="tabs">
              <button className={mode === "product" ? "active" : ""} onClick={() => setMode("product")}>Product</button>
              <button className={mode === "shorts" ? "active" : ""} onClick={() => setMode("shorts")}>Shorts</button>
              <button className={mode === "youtube" ? "active" : ""} onClick={() => setMode("youtube")}>YouTube</button>
            </div>

            <label>Topic</label>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />

            <label>Niche</label>
            <input value={niche} onChange={(e) => setNiche(e.target.value)} />

            <label>Tone</label>
            <input value={tone} onChange={(e) => setTone(e.target.value)} />

            <label>Buyer</label>
            <input value={buyer} onChange={(e) => setBuyer(e.target.value)} />

            <label>Promise</label>
            <input value={promise} onChange={(e) => setPromise(e.target.value)} />

            <label>Bonus</label>
            <input value={bonus} onChange={(e) => setBonus(e.target.value)} />

            <label>Notes</label>
            <textarea rows={5} value={notes} onChange={(e) => setNotes(e.target.value)} />

            <label>Shorts Duration</label>
            <input
              type="number"
              min={10}
              max={90}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />

            <button className="generate" onClick={generate} disabled={loading}>
              {loading ? "Generating..." : "Generate"}
            </button>

            <div className="status">{status}</div>

            {fileUrl ? (
              <a className="download" href={fileUrl} target="_blank" rel="noreferrer">
                Open generated file
              </a>
            ) : null}
          </section>

          <section className="panel">
            <h2>Output</h2>
            <textarea className="output" value={output} readOnly />
          </section>
        </div>
      </div>
    </main>
  );
}
