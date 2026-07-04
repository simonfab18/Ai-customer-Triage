import { getApiBaseUrl } from "@/lib/config";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-slate-950">
      <section className="mx-auto flex max-w-5xl flex-col gap-8">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            MVP foundation
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Support Triage</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
            The frontend shell is ready. Upcoming milestones will add organizations, Gmail import,
            AI triage, reply approval, and Gmail draft creation.
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold">API connection</h2>
          <p className="mt-2 text-sm text-slate-600">
            Configured API base URL: <span className="font-mono">{getApiBaseUrl()}</span>
          </p>
        </div>
      </section>
    </main>
  );
}

