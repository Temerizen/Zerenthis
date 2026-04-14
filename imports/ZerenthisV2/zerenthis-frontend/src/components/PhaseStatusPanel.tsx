import { fetchAPI } from "@/lib/api";

export default async function PhaseStatusPanel() {
  const data = await fetchAPI("/api/phase/verify");

  return (
    <div className="p-4 border border-cyan-500 rounded">
      <h2 className="text-lg font-semibold text-cyan-400 mb-4">Phase Status</h2>
      <div className="text-sm">
        <div className="mb-2">
          Verification:{" "}
          <span className={data.passed ? "text-green-400" : "text-red-400"}>
            {data.status}
          </span>
        </div>

        <div className="space-y-1 text-gray-300">
          {Object.entries(data.checks || {}).map(([key, value]) => (
            <div key={key}>
              {String(value) === "true" ? "✅" : "❌"} {key}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
