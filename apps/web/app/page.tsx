import Link from "next/link";

import { getApiBaseUrl } from "@/lib/config";

const urgencyRows = [
  { label: "Critical", value: "Payment failed before launch", color: "bg-urgency-critical", width: "w-[34%]" },
  { label: "High", value: "Refund request from VIP account", color: "bg-urgency-high", width: "w-[26%]" },
  { label: "Medium", value: "Shipping question needs reply", color: "bg-urgency-medium", width: "w-[24%]" },
  { label: "Low", value: "General product feedback", color: "bg-urgency-low", width: "w-[16%]" },
];

const workflow = [
  "Connect Gmail securely",
  "Import and classify email threads",
  "Review Gemini suggestions",
  "Approve drafts before sending",
];

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-50 text-slate-950">
      <section className="relative border-b border-slate-200 bg-white">
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-teal-50 via-slate-50/60 to-white" />
        <nav className="relative mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-900 font-display text-sm font-semibold text-white">TL</span>
            <span>
              <span className="block font-display text-base font-semibold tracking-tight">TriageLab</span>
              <span className="block text-xs text-slate-500">AI support operations</span>
            </span>
          </Link>
          <div className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <a href="#workflow" className="hover:text-slate-950">Workflow</a>
            <a href="#security" className="hover:text-slate-950">Security</a>
            <a href="#preview" className="hover:text-slate-950">Product</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="hidden rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 sm:inline-flex">Sign in</Link>
            <Link href="/dashboard" className="inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-sm shadow-teal-900/10 transition hover:bg-brand-700">Open app</Link>
          </div>
        </nav>

        <div className="relative mx-auto grid max-w-7xl gap-12 px-6 pb-16 pt-10 lg:grid-cols-[1fr_0.92fr] lg:px-8 lg:pb-24 lg:pt-16">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-sm font-medium text-teal-800">
              <span className="h-2 w-2 rounded-full bg-brand-600" /> Human-approved AI replies
            </div>
            <h1 className="mt-6 font-display text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
              Turn Gmail support chaos into a calm triage queue.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              TriageLab helps teams import Gmail conversations, classify urgency with Gemini, and approve polished replies before drafts are created in Gmail.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/login" className="inline-flex items-center justify-center rounded-md bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800">Start triaging</Link>
              <Link href="/dashboard" className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50">View dashboard</Link>
            </div>
            <div className="mt-10 grid max-w-xl grid-cols-3 overflow-hidden rounded-lg border border-slate-200 bg-white">
              <div className="p-4">
                <p className="font-display text-2xl font-semibold">4</p>
                <p className="mt-1 text-xs text-slate-500">Urgency levels</p>
              </div>
              <div className="border-l border-slate-200 p-4">
                <p className="font-display text-2xl font-semibold">3</p>
                <p className="mt-1 text-xs text-slate-500">Team roles</p>
              </div>
              <div className="border-l border-slate-200 p-4">
                <p className="font-display text-2xl font-semibold">0</p>
                <p className="mt-1 text-xs text-slate-500">Auto-sends</p>
              </div>
            </div>
          </div>

          <div id="preview" className="rounded-xl border border-slate-200 bg-white p-3 shadow-2xl shadow-slate-900/10">
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-4 border-b border-slate-200 pb-4">
                <div>
                  <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Live queue</p>
                  <h2 className="mt-1 font-display text-xl font-semibold">Priority distribution</h2>
                </div>
                <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">Gmail connected</span>
              </div>
              <div className="mt-5 flex h-3 overflow-hidden rounded-full bg-slate-200">
                {urgencyRows.map((row) => <span key={row.label} className={`${row.color} ${row.width}`} />)}
              </div>
              <div className="mt-5 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
                {urgencyRows.map((row) => (
                  <div key={row.label} className="grid grid-cols-[auto_1fr_auto] items-center gap-3 p-4">
                    <span className={`h-10 w-1.5 rounded-full ${row.color}`} />
                    <div>
                      <p className="font-medium text-slate-900">{row.value}</p>
                      <p className="mt-1 text-sm text-slate-500">AI category, sentiment, and suggested action ready</p>
                    </div>
                    <span className="rounded-md border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600">{row.label}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-lg border border-teal-200 bg-teal-50 p-4">
                <p className="text-sm font-semibold text-teal-900">Suggested reply</p>
                <p className="mt-2 text-sm leading-6 text-teal-800">Apologize, confirm the order details, and offer an expedited replacement after the agent approves the draft.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-7xl px-6 py-14 lg:px-8">
        <div className="grid gap-5 md:grid-cols-4">
          {workflow.map((step, index) => (
            <div key={step} className="rounded-lg border border-slate-200 bg-white p-5">
              <p className="font-mono text-xs text-slate-500">0{index + 1}</p>
              <h2 className="mt-4 font-display text-lg font-semibold text-slate-900">{step}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">A focused step in the support workflow, designed to keep agents in control and customers moving.</p>
            </div>
          ))}
        </div>
      </section>

      <section id="security" className="border-y border-slate-200 bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-6 py-14 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <div>
            <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Built for operators</p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight">Clean controls for real support teams.</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              "Multi-tenant workspace isolation",
              "Owner, admin, and agent roles",
              "Encrypted Gmail OAuth storage",
              "Approval required before draft creation",
            ].map((item) => (
              <div key={item} className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm font-medium text-slate-700">{item}</div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-10 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <p>API status: <span className="font-mono text-slate-700">{getApiBaseUrl()}</span></p>
        <Link href="/login" className="font-medium text-teal-700 hover:text-teal-800">Sign in to continue</Link>
      </section>
    </main>
  );
}
