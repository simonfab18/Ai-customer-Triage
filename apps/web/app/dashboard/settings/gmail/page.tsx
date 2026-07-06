import { GmailConnectionPanel } from "@/features/gmail/components/GmailConnectionPanel";
import { SettingsNav } from "@/features/settings/components/SettingsNav";

export default function GmailSettingsPage() {
  return (
    <section className="space-y-6">
      <div>
        <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Integrations</p>
        <h2 className="font-display text-3xl font-semibold tracking-tight text-slate-900">Gmail</h2>
        <p className="mt-2 max-w-2xl text-slate-600">Connect a support mailbox, import support email, and monitor recent import jobs.</p>
      </div>
      <SettingsNav />
      <GmailConnectionPanel />
    </section>
  );
}