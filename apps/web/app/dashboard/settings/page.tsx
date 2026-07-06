import { GmailConnectionPanel } from "@/features/gmail/components/GmailConnectionPanel";
import { SettingsNav } from "@/features/settings/components/SettingsNav";

export default function SettingsPage() {
  return (
    <section className="space-y-6">
      <div>
        <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Owner/Admin</p>
        <h2 className="font-display text-3xl font-semibold tracking-tight text-slate-900">Settings</h2>
        <p className="mt-2 max-w-2xl text-slate-600">Manage integrations, teammates, and workspace defaults for your support operation.</p>
      </div>
      <SettingsNav />
      <GmailConnectionPanel />
    </section>
  );
}