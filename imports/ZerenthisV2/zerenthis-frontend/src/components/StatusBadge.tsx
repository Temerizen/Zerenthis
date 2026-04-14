export default function StatusBadge({ status }: { status: "live" | "partial" | "locked" }) {
  const colors = {
    live: "bg-green-500",
    partial: "bg-yellow-500",
    locked: "bg-red-500"
  };

  return (
    <span className={`px-2 py-1 text-xs rounded ${colors[status]}`}>
      {status.toUpperCase()}
    </span>
  );
}
