"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { StatusBadge, UrgencyBadge } from "@/components/ui/Badges";
import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { createClient } from "@/lib/supabase/client";
import {
  approveReplySuggestion,
  createGmailDraftFromSuggestion,
  getReplySuggestions,
  getTicket,
  getTicketEvents,
  getTicketTriageResults,
  rejectReplySuggestion,
  runTicketTriage,
  updateReplySuggestion,
} from "../api";
import type { AITriageResult, ReplySuggestion, Ticket, TicketEvent } from "../types";

function displayStatus(status: string) {
  return status.replaceAll("_", " ");
}

export function TicketDetailClient({ ticketId }: { ticketId: string }) {
  const supabase = createClient();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [events, setEvents] = useState<TicketEvent[]>([]);
  const [triageResults, setTriageResults] = useState<AITriageResult[]>([]);
  const [replySuggestions, setReplySuggestions] = useState<ReplySuggestion[]>([]);
  const [replyText, setReplyText] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState(false);
  const [savingReply, setSavingReply] = useState(false);
  const [approvingReply, setApprovingReply] = useState(false);
  const [rejectingReply, setRejectingReply] = useState(false);
  const [creatingDraft, setCreatingDraft] = useState(false);

  async function getSessionContext() {
    const organizationId = getStoredOrganizationId();
    const { data } = await supabase.auth.getSession();
    if (!organizationId || !data.session) return null;
    return { organizationId, accessToken: data.session.access_token };
  }

  async function loadTicket() {
    setLoading(true);
    setMessage(null);
    const context = await getSessionContext();
    if (!context) {
      setMessage("Select an organization and sign in before viewing tickets.");
      setLoading(false);
      return;
    }

    try {
      const [loadedTicket, loadedEvents, loadedResults, loadedSuggestions] = await Promise.all([
        getTicket(context.organizationId, ticketId, context.accessToken),
        getTicketEvents(context.organizationId, ticketId, context.accessToken),
        getTicketTriageResults(context.organizationId, ticketId, context.accessToken),
        getReplySuggestions(context.organizationId, ticketId, context.accessToken),
      ]);
      setTicket(loadedTicket);
      setEvents(loadedEvents);
      setTriageResults(loadedResults);
      setReplySuggestions(loadedSuggestions);
      const latestSuggestion = loadedSuggestions[0];
      setReplyText(latestSuggestion?.edited_body ?? latestSuggestion?.body ?? "");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load ticket.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunTriage() {
    const context = await getSessionContext();
    if (!context) return;
    setTriaging(true);
    setMessage(null);
    try {
      await runTicketTriage(context.organizationId, ticketId, context.accessToken);
      await loadTicket();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to run AI triage.");
    } finally {
      setTriaging(false);
    }
  }

  async function handleSaveReply() {
    const latestSuggestion = replySuggestions[0];
    const context = await getSessionContext();
    if (!latestSuggestion || !context) return;
    setSavingReply(true);
    setMessage(null);
    try {
      await updateReplySuggestion(context.organizationId, latestSuggestion.id, context.accessToken, replyText);
      await loadTicket();
      setMessage("Reply edits saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to save reply.");
    } finally {
      setSavingReply(false);
    }
  }

  async function handleApproveReply() {
    const latestSuggestion = replySuggestions[0];
    const context = await getSessionContext();
    if (!latestSuggestion || !context) return;
    setApprovingReply(true);
    setMessage(null);
    try {
      if ((latestSuggestion.edited_body ?? latestSuggestion.body) !== replyText) {
        await updateReplySuggestion(context.organizationId, latestSuggestion.id, context.accessToken, replyText);
      }
      await approveReplySuggestion(context.organizationId, latestSuggestion.id, context.accessToken);
      await loadTicket();
      setMessage("Reply approved. Draft creation is now available.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to approve reply.");
    } finally {
      setApprovingReply(false);
    }
  }

  async function handleRejectReply() {
    const latestSuggestion = replySuggestions[0];
    const context = await getSessionContext();
    if (!latestSuggestion || !context) return;
    setRejectingReply(true);
    setMessage(null);
    try {
      await rejectReplySuggestion(context.organizationId, latestSuggestion.id, context.accessToken);
      await loadTicket();
      setMessage("Reply suggestion rejected.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to reject reply.");
    } finally {
      setRejectingReply(false);
    }
  }

  async function handleCreateDraft() {
    const latestSuggestion = replySuggestions[0];
    const context = await getSessionContext();
    if (!latestSuggestion || !context) return;
    setCreatingDraft(true);
    setMessage(null);
    try {
      const result = await createGmailDraftFromSuggestion(context.organizationId, latestSuggestion.id, context.accessToken);
      await loadTicket();
      setMessage(`Gmail draft created: ${result.gmail_draft_id}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to create Gmail draft.");
    } finally {
      setCreatingDraft(false);
    }
  }

  useEffect(() => {
    void loadTicket();
  }, [ticketId]);

  const latestTriage = triageResults[0];
  const latestSuggestion = replySuggestions[0];
  const canEdit = latestSuggestion?.status === "suggested" || latestSuggestion?.status === "edited";
  const canDraft = latestSuggestion?.status === "approved";

  if (loading) return <p className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">Loading ticket...</p>;

  return (
    <section className="space-y-5">
      <Link href="/dashboard/tickets" className="text-sm font-medium text-slate-600 hover:text-slate-900">Back to queue</Link>
      {message ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">{message}</p> : null}

      {ticket ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_420px]">
          <article className="min-h-[calc(100vh-160px)] rounded-lg border border-slate-200 bg-white">
            <div className="border-b border-slate-200 p-5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-mono text-xs text-slate-500">{ticket.id}</p>
                  <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight text-slate-900">{ticket.subject}</h2>
                  <p className="mt-2 text-sm text-slate-500">From {ticket.customer.name ?? ticket.customer.email} - {new Date(ticket.received_at).toLocaleString()}</p>
                </div>
                <div className="flex flex-wrap gap-2"><UrgencyBadge priority={ticket.priority} /><StatusBadge status={ticket.status} /></div>
              </div>
            </div>
            <div className="max-h-[calc(100vh-280px)] overflow-y-auto p-5">
              <div className="rounded-lg bg-slate-50 p-5 text-sm leading-7 text-slate-700">
                <p className="whitespace-pre-wrap">{ticket.message_text}</p>
              </div>
              <div className="mt-6">
                <h3 className="font-display text-lg font-semibold">Timeline</h3>
                <div className="mt-3 divide-y divide-slate-100 rounded-lg border border-slate-200">
                  {events.map((event) => (
                    <div key={event.id} className="grid gap-2 p-3 text-sm sm:grid-cols-[1fr_auto]">
                      <span className="font-medium text-slate-700">{event.event_type.replaceAll("_", " ")}</span>
                      <span className="font-mono text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </article>

          <aside className="space-y-4 lg:sticky lg:top-28 lg:self-start">
            <div className="rounded-lg border border-slate-200 bg-white p-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="font-display text-lg font-semibold">AI classification</h2>
                <Button type="button" variant="outline" onClick={() => void handleRunTriage()} disabled={triaging}>{triaging ? "Running..." : "Regenerate"}</Button>
              </div>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div><dt className="text-slate-500">Urgency</dt><dd className="mt-1"><UrgencyBadge priority={ticket.priority} /></dd></div>
                <div><dt className="text-slate-500">Category</dt><dd className="mt-1 font-medium capitalize">{ticket.category.replaceAll("_", " ")}</dd></div>
                <div><dt className="text-slate-500">Confidence</dt><dd className="mt-1 font-mono text-slate-600">N/A</dd></div>
                <div><dt className="text-slate-500">Review</dt><dd className="mt-1 font-medium">{latestTriage?.requires_human_review ? "Required" : "Not flagged"}</dd></div>
              </dl>
              {latestTriage ? (
                <div className="mt-4 border-t border-slate-200 pt-4 text-sm">
                  <p className="font-medium">Reasoning</p>
                  <p className="mt-1 text-slate-600">{latestTriage.summary}</p>
                  <p className="mt-3 font-medium">Suggested action</p>
                  <p className="mt-1 text-slate-600">{latestTriage.suggested_action}</p>
                </div>
              ) : <p className="mt-4 text-sm text-slate-500">No AI triage result yet.</p>}
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-5">
              <h2 className="font-display text-lg font-semibold">Suggested reply</h2>
              {!latestSuggestion ? <p className="mt-3 text-sm text-slate-500">Run triage to generate an editable reply.</p> : (
                <div className="mt-4 space-y-4">
                  <div className="flex items-center justify-between rounded-md bg-slate-50 p-3 text-sm">
                    <span className="capitalize text-slate-600">{displayStatus(latestSuggestion.status)}</span>
                    <span className="font-mono text-xs text-slate-500">{latestSuggestion.created_by}</span>
                  </div>
                  <textarea value={replyText} onChange={(event) => setReplyText(event.target.value)} disabled={!canEdit} rows={12} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm leading-6 outline-none focus:border-slate-900 disabled:bg-slate-50" />
                  <div className="grid gap-2 sm:grid-cols-2">
                    <Button type="button" variant="outline" onClick={() => void handleSaveReply()} disabled={!canEdit || savingReply}>{savingReply ? "Saving..." : "Save"}</Button>
                    <Button type="button" variant="primary" onClick={() => void handleApproveReply()} disabled={!canEdit || approvingReply}>{approvingReply ? "Approving..." : "Approve"}</Button>
                    <Button type="button" variant="danger" onClick={() => void handleRejectReply()} disabled={!canEdit || rejectingReply}>{rejectingReply ? "Rejecting..." : "Reject"}</Button>
                    <Button type="button" variant="primary" onClick={() => void handleCreateDraft()} disabled={!canDraft || creatingDraft}>{creatingDraft ? "Creating..." : "Create draft"}</Button>
                  </div>
                </div>
              )}
            </div>
          </aside>
        </div>
      ) : null}
    </section>
  );
}