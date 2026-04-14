import { fetchAPI } from "@/lib/api";

export default async function TrafficPage() {
  const queueData = await fetchAPI("/api/posting/plan");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Traffic</h1>

      <div className="p-4 border border-cyan-500 rounded">
        <h2 className="text-lg font-semibold text-cyan-400 mb-4">Queue Planner</h2>
        <div className="text-gray-300 text-sm space-y-2">
          <div>Status: {queueData.status}</div>
          <div>Topic: {queueData.decision?.topic || "none"}</div>
          <div>Active Queue: {queueData.decision?.active_queue ?? "n/a"}</div>
          <div>Priority Score: {queueData.decision?.priority_score ?? "n/a"}</div>
          <div>Needs Refill: {String(queueData.decision?.needs_refill)}</div>
          <div>Cooldown OK: {String(queueData.decision?.cooldown_ok)}</div>
        </div>
      </div>
    </div>
  );
}
