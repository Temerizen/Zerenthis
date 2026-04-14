import StatusBadge from "@/components/StatusBadge";

export default function CosmicMap() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Cosmic Map</h1>

      <div className="space-y-4">
        <div className="p-4 border border-cyan-500">
          Core Engine <StatusBadge status="live" />
        </div>

        <div className="p-4 border border-cyan-500">
          Reality Engine <StatusBadge status="live" />
        </div>

        <div className="p-4 border border-cyan-500">
          Money System <StatusBadge status="partial" />
        </div>

        <div className="p-4 border border-cyan-500">
          Market Intelligence <StatusBadge status="locked" />
        </div>
      </div>
    </div>
  );
}
