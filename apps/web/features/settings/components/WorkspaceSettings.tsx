"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";

export function WorkspaceSettings() {
  const [signature, setSignature] = useState("Best regards,\nCustomer Support Team");
  const [message, setMessage] = useState<string | null>(null);

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="font-display text-lg font-semibold">Workspace preferences</h2>
        <p className="mt-2 text-sm text-slate-500">These controls are UI-ready. The backend does not yet persist signature or preference fields.</p>
        <label className="mt-5 block text-sm font-medium text-slate-700" htmlFor="signature">Default reply signature</label>
        <textarea id="signature" value={signature} onChange={(event) => setSignature(event.target.value)} rows={6} className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm leading-6 outline-none focus:border-slate-900" />
        <Button type="button" variant="primary" className="mt-4" onClick={() => setMessage("Preference storage needs a backend workspace settings table before this can save.")}>Save preferences</Button>
        {message ? <p className="mt-4 text-sm text-slate-600">{message}</p> : null}
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="font-display text-lg font-semibold">Pilot defaults</h2>
        <dl className="mt-4 space-y-3 text-sm">
          <div><dt className="text-slate-500">Draft policy</dt><dd className="font-medium">Human approval required</dd></div>
          <div><dt className="text-slate-500">Urgency colors</dt><dd className="font-medium">Critical, high, medium, low</dd></div>
          <div><dt className="text-slate-500">AI confidence</dt><dd className="font-medium">Backend field needed</dd></div>
        </dl>
      </div>
    </div>
  );
}