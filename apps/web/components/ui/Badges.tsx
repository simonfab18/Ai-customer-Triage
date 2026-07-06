import { cx } from "./cx";

export function UrgencyRail({ priority, className }: { priority: string; className?: string }) {
  const color =
    priority === "critical"
      ? "bg-urgency-critical"
      : priority === "high"
        ? "bg-urgency-high"
        : priority === "medium"
          ? "bg-urgency-medium"
          : "bg-urgency-low";
  return <span className={cx("block w-1.5 rounded-full", color, className)} aria-hidden="true" />;
}

export function UrgencyBadge({ priority }: { priority: string }) {
  const styles =
    priority === "critical"
      ? "border-rose-200 bg-rose-50 text-rose-700 before:bg-urgency-critical"
      : priority === "high"
        ? "border-amber-200 bg-amber-50 text-amber-700 before:bg-urgency-high"
        : priority === "medium"
          ? "border-blue-200 bg-blue-50 text-blue-700 before:bg-urgency-medium"
          : "border-slate-200 bg-slate-50 text-slate-600 before:bg-urgency-low";
  return (
    <span className={cx("inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium capitalize before:h-2 before:w-2 before:rounded-full", styles)}>
      {priority}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const styles =
    status === "resolved"
      ? "border-teal-200 bg-teal-50 text-teal-700"
      : status === "spam"
        ? "border-slate-300 bg-slate-100 text-slate-600"
        : status === "draft_created"
          ? "border-teal-200 bg-teal-50 text-teal-700"
          : "border-slate-200 bg-white text-slate-600";
  return <span className={cx("inline-flex rounded-md border px-2 py-1 text-xs font-medium capitalize", styles)}>{status.replaceAll("_", " ")}</span>;
}