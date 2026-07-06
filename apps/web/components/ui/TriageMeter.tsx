import type { MetricsOverview } from "@/features/tickets/types";

const segments = [
  { key: "critical", label: "Critical", className: "bg-urgency-critical" },
  { key: "high", label: "High", className: "bg-urgency-high" },
  { key: "medium", label: "Medium", className: "bg-urgency-medium" },
  { key: "low", label: "Low", className: "bg-urgency-low" },
];

export function TriageMeter({ metrics }: { metrics: MetricsOverview }) {
  const total = Math.max(1, Object.values(metrics.by_priority).reduce((sum, count) => sum + count, 0));

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-lg font-semibold text-slate-900">Triage meter</h2>
          <p className="text-sm text-slate-500">Urgency distribution across this workspace.</p>
        </div>
        <p className="font-mono text-xs text-slate-500">{total === 1 && metrics.total_tickets === 0 ? 0 : total} tickets</p>
      </div>
      <div className="mt-4 flex h-3 overflow-hidden rounded-full bg-slate-100">
        {segments.map((segment) => {
          const count = metrics.by_priority[segment.key] ?? 0;
          return <span key={segment.key} className={segment.className} style={{ width: `${(count / total) * 100}%` }} />;
        })}
      </div>
      <div className="mt-4 grid gap-2 sm:grid-cols-4">
        {segments.map((segment) => (
          <div key={segment.key} className="flex items-center justify-between text-xs text-slate-600">
            <span className="flex items-center gap-2"><span className={`h-2 w-2 rounded-full ${segment.className}`} />{segment.label}</span>
            <span className="font-mono">{metrics.by_priority[segment.key] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}