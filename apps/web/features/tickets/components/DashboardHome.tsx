"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { TriageMeter } from "@/components/ui/TriageMeter";
import { StatCard } from "@/components/ui/StatCard";
import { Button } from "@/components/ui/Button";
import { StatusBadge, UrgencyBadge } from "@/components/ui/Badges";
import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { getGmailConnections } from "@/lib/api-client";
import { createClient } from "@/lib/supabase/client";
import { getMetricsOverview, getReplySuggestions, getTickets } from "@/features/tickets/api";
import type { MetricsOverview, ReplySuggestion, TicketListItem } from "@/features/tickets/types";

const ONBOARDING_KEY = "support-triage:onboarding-dismissed";

function completionSteps(hasGmail: boolean, hasTickets: boolean, hasApproved: boolean) {
  return [
    { label: "Connect Gmail", done: hasGmail, href: "/dashboard/settings" },
    { label: "Import emails", done: hasTickets, href: "/dashboard/settings" },
    { label: "Approve first reply", done: hasApproved, href: "/dashboard/tickets" },
    { label: "Invite teammate", done: false, href: "/dashboard/settings/team" },
  ];
}

export function DashboardHome() {
  const supabase = createClient();
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null);
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [suggestions, setSuggestions] = useState<ReplySuggestion[]>([]);
  const [hasGmail, setHasGmail] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setDismissed(window.localStorage.getItem(ONBOARDING_KEY) === "true");

    async function load() {
      const organizationId = getStoredOrganizationId();
      const { data } = await supabase.auth.getSession();
      const accessToken = data.session?.access_token;
      if (!organizationId || !accessToken) {
        setMessage("Select an organization and sign in to load your dashboard.");
        return;
      }

      try {
        const [metricData, ticketData, gmailConnections] = await Promise.all([
          getMetricsOverview(organizationId, accessToken),
          getTickets(organizationId, accessToken),
          getGmailConnections(accessToken, organizationId),
        ]);
        setMetrics(metricData);
        setTickets(ticketData.slice(0, 5));
        setHasGmail(gmailConnections.some((connection) => connection.status === "active"));

        const pendingSuggestions = await Promise.all(
          ticketData.slice(0, 8).map(async (ticket) => {
            try {
              return await getReplySuggestions(organizationId, ticket.id, accessToken);
            } catch {
              return [];
            }
          }),
        );
        setSuggestions(pendingSuggestions.flat().filter((suggestion) => suggestion.status === "suggested" || suggestion.status === "edited"));
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to load dashboard.");
      }
    }

    void load();
  }, [supabase]);

  const steps = useMemo(
    () => completionSteps(hasGmail, tickets.length > 0, metrics ? metrics.draft_created_tickets > 0 : false),
    [hasGmail, tickets.length, metrics],
  );
  const progress = steps.filter((step) => step.done).length;

  function dismissOnboarding() {
    window.localStorage.setItem(ONBOARDING_KEY, "true");
    setDismissed(true);
  }

  if (message) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
        {message} <Link href="/dashboard/organizations" className="font-medium text-teal-700 underline">Go to organizations</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Today</p>
          <h2 className="mt-2 font-display text-3xl font-semibold tracking-tight text-slate-900">Good to see you. The queue is sorted by severity.</h2>
          <p className="mt-3 max-w-2xl text-slate-600">Critical and high-priority tickets rise first, AI suggestions stay human-approved, and Gmail drafts are only created after approval.</p>
          {metrics ? (
            <div className="mt-6 grid overflow-hidden rounded-lg border border-slate-200 sm:grid-cols-4">
              <StatCard label="Open tickets" value={metrics.active_tickets} />
              <StatCard label="Pending approval" value={suggestions.length} />
              <StatCard label="Auto-triaged today" value={metrics.total_tickets} detail="Imported ticket total" />
              <StatCard label="Avg AI confidence" value="N/A" detail="Backend field needed" />
            </div>
          ) : null}
        </div>
        {metrics ? <TriageMeter metrics={metrics} /> : <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500">Loading triage meter...</div>}
      </section>

      {!dismissed ? (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-display text-lg font-semibold">Pilot setup checklist</h2>
              <p className="mt-1 text-sm text-slate-500">{progress} of {steps.length} complete</p>
            </div>
            <Button variant="ghost" onClick={dismissOnboarding}>Dismiss</Button>
          </div>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-brand-600" style={{ width: `${(progress / steps.length) * 100}%` }} />
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-4">
            {steps.map((step) => (
              <Link key={step.label} href={step.href} className="rounded-md border border-slate-200 p-3 text-sm hover:border-slate-300">
                <span className={step.done ? "text-teal-700" : "text-slate-500"}>{step.done ? "Done" : "Next"}</span>
                <span className="mt-1 block font-medium text-slate-900">{step.label}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-display text-lg font-semibold">Needs approval</h2>
          </div>
          {suggestions.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">Nothing waiting on you. Check back after the next import or triage run.</p>
          ) : (
            <div className="divide-y divide-slate-100">
              {suggestions.slice(0, 5).map((suggestion) => (
                <Link key={suggestion.id} href={`/dashboard/tickets/${suggestion.ticket_id}`} className="block px-5 py-4 text-sm hover:bg-slate-50">
                  <p className="font-medium text-slate-900">{suggestion.edited_body ?? suggestion.body}</p>
                  <p className="mt-1 font-mono text-xs text-slate-500">{suggestion.id}</p>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-display text-lg font-semibold">Latest active tickets</h2>
          </div>
          {tickets.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">Nothing waiting on you. Check back later.</p>
          ) : (
            <div className="divide-y divide-slate-100">
              {tickets.map((ticket) => (
                <Link key={ticket.id} href={`/dashboard/tickets/${ticket.id}`} className="grid gap-3 px-5 py-4 text-sm hover:bg-slate-50 sm:grid-cols-[1fr_auto]">
                  <div>
                    <p className="font-medium text-slate-900">{ticket.subject}</p>
                    <p className="mt-1 text-slate-500">{ticket.customer_name ?? ticket.customer_email}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <UrgencyBadge priority={ticket.priority} />
                    <StatusBadge status={ticket.status} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
