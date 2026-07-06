import Link from "next/link";

import { getApiBaseUrl } from "@/lib/config";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-slate-950">
      <section className="mx-auto flex max-w-5xl flex-col gap-8">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            AI customer support triage
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold tracking-tight">
            Customer Support Triage and Response
          </h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
            Connect Gmail, import customer emails, prioritize urgent tickets with Gemini, and let
            human agents approve replies before Gmail drafts are created.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
            >
              Sign in
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400"
            >
              Open dashboard
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-display text-base font-semibold">System status</h2>
          <p className="mt-2 text-sm text-slate-600">
            Configured API base URL: <span className="font-mono">{getApiBaseUrl()}</span>
          </p>
        </div>
      </section>
    </main>
  );
}
