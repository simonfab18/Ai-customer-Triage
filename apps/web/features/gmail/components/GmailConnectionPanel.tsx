"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { getGmailConnections, getRecentImports, queueGmailSync, startGmailOAuth, syncGmailConnection } from "@/lib/api-client";
import type { GmailConnection, JobRun } from "@/lib/api-types";
import { createClient } from "@/lib/supabase/client";

export function GmailConnectionPanel() {
  const supabase = createClient();
  const [connections, setConnections] = useState<GmailConnection[]>([]);
  const [imports, setImports] = useState<JobRun[]>([]);
  const [organizationId, setOrganizationId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [syncingConnectionId, setSyncingConnectionId] = useState<string | null>(null);
  const [queueingConnectionId, setQueueingConnectionId] = useState<string | null>(null);

  async function getAccessToken() {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  }

  async function loadConnections() {
    setLoading(true);
    setMessage(null);
    const selectedOrganizationId = getStoredOrganizationId();
    setOrganizationId(selectedOrganizationId);

    if (!selectedOrganizationId) {
      setMessage("Select or create an organization first.");
      setLoading(false);
      return;
    }

    const accessToken = await getAccessToken();
    if (!accessToken) {
      setMessage("Sign in before connecting Gmail.");
      setLoading(false);
      return;
    }

    try {
      const [connectionData, importData] = await Promise.all([
        getGmailConnections(accessToken, selectedOrganizationId),
        getRecentImports(accessToken, selectedOrganizationId),
      ]);
      setConnections(connectionData);
      setImports(importData);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load Gmail connections.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadConnections();
  }, []);

  async function handleConnect() {
    if (!organizationId) {
      setMessage("Select or create an organization first.");
      return;
    }

    const accessToken = await getAccessToken();
    if (!accessToken) {
      setMessage("Sign in before connecting Gmail.");
      return;
    }

    setConnecting(true);
    setMessage(null);

    try {
      const { auth_url } = await startGmailOAuth(accessToken, organizationId);
      window.location.href = auth_url;
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to start Gmail OAuth.");
      setConnecting(false);
    }
  }

  async function handleSync(connectionId: string) {
    if (!organizationId) {
      setMessage("Select or create an organization first.");
      return;
    }

    const accessToken = await getAccessToken();
    if (!accessToken) {
      setMessage("Sign in before importing Gmail.");
      return;
    }

    setSyncingConnectionId(connectionId);
    setMessage(null);

    try {
      const job = await syncGmailConnection(accessToken, organizationId, connectionId);
      setMessage(
        `Import ${job.status}: imported ${String(job.job_metadata.imported_count ?? 0)}, skipped ${String(
          job.job_metadata.skipped_count ?? 0,
        )}.`,
      );
      await loadConnections();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to import Gmail messages.");
    } finally {
      setSyncingConnectionId(null);
    }
  }

  async function handleQueueSync(connectionId: string) {
    if (!organizationId) {
      setMessage("Select or create an organization first.");
      return;
    }

    const accessToken = await getAccessToken();
    if (!accessToken) {
      setMessage("Sign in before queueing Gmail import.");
      return;
    }

    setQueueingConnectionId(connectionId);
    setMessage(null);

    try {
      const job = await queueGmailSync(accessToken, organizationId, connectionId);
      setMessage(`Queued import job ${job.id}. Status: ${job.status}.`);
      await loadConnections();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to queue Gmail import.");
    } finally {
      setQueueingConnectionId(null);
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Gmail connection</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Connect a Gmail mailbox, import messages immediately, or queue import jobs for the worker.
          </p>
        </div>
        <button
          type="button"
          onClick={handleConnect}
          disabled={connecting || !organizationId}
          className="rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white disabled:bg-slate-400"
        >
          {connecting ? "Connecting..." : "Connect Gmail"}
        </button>
      </div>

      {message ? (
        <div className="mt-5 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          {message}{" "}
          {!organizationId ? (
            <Link href="/dashboard/organizations" className="font-medium text-slate-950 underline">
              Go to organizations
            </Link>
          ) : null}
        </div>
      ) : null}

      <div className="mt-6">
        <h3 className="text-sm font-semibold">Connected accounts</h3>
        {loading ? <p className="mt-3 text-sm text-slate-600">Loading...</p> : null}
        {!loading && connections.length === 0 ? (
          <p className="mt-3 text-sm text-slate-600">No Gmail account connected yet.</p>
        ) : null}
        <div className="mt-3 space-y-3">
          {connections.map((connection) => (
            <div key={connection.id} className="rounded-md border border-slate-200 p-4 text-sm">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium">{connection.gmail_email}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Status: {connection.status}
                    {connection.last_sync_at ? ` - Last sync: ${new Date(connection.last_sync_at).toLocaleString()}` : ""}
                  </p>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => handleSync(connection.id)}
                    disabled={syncingConnectionId === connection.id || queueingConnectionId === connection.id}
                    className="rounded-md border border-slate-300 px-3 py-2 text-xs font-medium text-slate-700 disabled:text-slate-400"
                  >
                    {syncingConnectionId === connection.id ? "Importing..." : "Import now"}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQueueSync(connection.id)}
                    disabled={syncingConnectionId === connection.id || queueingConnectionId === connection.id}
                    className="rounded-md bg-slate-950 px-3 py-2 text-xs font-medium text-white disabled:bg-slate-400"
                  >
                    {queueingConnectionId === connection.id ? "Queueing..." : "Queue import"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-semibold">Recent imports</h3>
          <button type="button" onClick={() => void loadConnections()} className="text-xs font-medium text-slate-600">
            Refresh
          </button>
        </div>
        {imports.length === 0 ? <p className="mt-3 text-sm text-slate-600">No imports yet.</p> : null}
        <div className="mt-3 space-y-2">
          {imports.map((job) => (
            <div key={job.id} className="rounded-md bg-slate-50 p-3 text-xs text-slate-600">
              <span className="font-medium text-slate-800">{job.status}</span>
              {" - "}
              imported {String(job.job_metadata.imported_count ?? 0)}, skipped {String(job.job_metadata.skipped_count ?? 0)}
              <span className="mt-1 block text-slate-500">Job {job.id}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
