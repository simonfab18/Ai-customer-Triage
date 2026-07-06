"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/StatCard";
import { TriageMeter } from "@/components/ui/TriageMeter";
import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { createClient } from "@/lib/supabase/client";
import { getMetricsOverview, getTickets } from "../api";
import type { MetricsOverview, TicketListItem } from "../types";
import { TicketList } from "./TicketList";

const urgencyOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };

export function TicketDashboard() {
  const supabase = createClient();
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [urgency, setUrgency] = useState("all");
  const [sort, setSort] = useState("urgency");

  async function loadTickets() {
    setLoading(true);
    setMessage(null);

    const organizationId = getStoredOrganizationId();
    if (!organizationId) {
      setMessage("Select an organization first.");
      setLoading(false);
      return;
    }

    const { data } = await supabase.auth.getSession();
    if (!data.session) {
      setMessage("Sign in before viewing tickets.");
      setLoading(false);
      return;
    }

    try {
      const [loadedTickets, loadedMetrics] = await Promise.all([
        getTickets(organizationId, data.session.access_token),
        getMetricsOverview(organizationId, data.session.access_token),
      ]);
      setTickets(loadedTickets);
      setMetrics(loadedMetrics);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load tickets.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTickets();
  }, []);

  const visibleTickets = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return tickets
      .filter((ticket) => urgency === "all" || ticket.priority === urgency)
      .filter((ticket) => {
        if (!normalizedQuery) return true;
        return [ticket.subject, ticket.customer_email, ticket.customer_name ?? "", ticket.category, ticket.status]
          .join(" ")
          .toLowerCase()
          .includes(normalizedQuery);
      })
      .sort((left, right) => {
        if (sort === "recent") return new Date(right.received_at).getTime() - new Date(left.received_at).getTime();
        return (urgencyOrder[left.priority] ?? 4) - (urgencyOrder[right.priority] ?? 4) || new Date(right.received_at).getTime() - new Date(left.received_at).getTime();
      });
  }, [tickets, query, urgency, sort]);

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Active queue</p>
          <h2 className="font-display text-3xl font-semibold tracking-tight text-slate-900">Triage queue</h2>
          <p className="mt-2 max-w-2xl text-slate-600">Filter by urgency, search across sender and subject, and keep the highest-risk tickets at the top.</p>
        </div>
        <Button type="button" onClick={() => void loadTickets()} variant="outline">Refresh</Button>
      </div>

      {message ? (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          {message} {message.includes("organization") ? <Link href="/dashboard/organizations" className="font-medium text-teal-700 underline">Go to organizations</Link> : null}
        </div>
      ) : null}

      {metrics ? (
        <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          <div className="grid overflow-hidden rounded-lg border border-slate-200 sm:grid-cols-3">
            <StatCard label="Active" value={metrics.active_tickets} />
            <StatCard label="Critical" value={metrics.critical_tickets} />
            <StatCard label="High" value={metrics.high_priority_tickets} />
          </div>
          <TriageMeter metrics={metrics} />
        </div>
      ) : null}

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto_auto]">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search subject, sender, category..."
            className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
          />
          <select value={urgency} onChange={(event) => setUrgency(event.target.value)} className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">
            <option value="all">All urgency</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select value={sort} onChange={(event) => setSort(event.target.value)} className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">
            <option value="urgency">Sort by urgency</option>
            <option value="recent">Sort by recency</option>
          </select>
        </div>
      </div>

      {loading ? <p className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">Loading tickets...</p> : <TicketList tickets={visibleTickets} />}
    </section>
  );
}