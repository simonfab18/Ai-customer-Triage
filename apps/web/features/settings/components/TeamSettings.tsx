"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { getMembers, inviteMember, updateMemberRole } from "@/lib/api-client";
import type { Member } from "@/lib/api-types";
import { createClient } from "@/lib/supabase/client";

export function TeamSettings() {
  const supabase = createClient();
  const [members, setMembers] = useState<Member[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("agent");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function context() {
    const organizationId = getStoredOrganizationId();
    const { data } = await supabase.auth.getSession();
    const accessToken = data.session?.access_token;
    if (!organizationId || !accessToken) return null;
    return { organizationId, accessToken };
  }

  async function loadMembers() {
    setLoading(true);
    setMessage(null);
    const ctx = await context();
    if (!ctx) {
      setMessage("Select an organization and sign in first.");
      setLoading(false);
      return;
    }
    try {
      setMembers(await getMembers(ctx.accessToken, ctx.organizationId));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load team.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadMembers();
  }, []);

  async function handleInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ctx = await context();
    if (!ctx) return;
    try {
      await inviteMember(ctx.accessToken, ctx.organizationId, email, role);
      setEmail("");
      await loadMembers();
      setMessage("Invitation created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to invite teammate.");
    }
  }

  async function handleRole(memberId: string, nextRole: string) {
    const ctx = await context();
    if (!ctx) return;
    try {
      await updateMemberRole(ctx.accessToken, ctx.organizationId, memberId, nextRole);
      await loadMembers();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to update role.");
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <div className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="font-display text-lg font-semibold">Team members</h2>
        </div>
        {loading ? <p className="p-5 text-sm text-slate-500">Loading team...</p> : null}
        <div className="divide-y divide-slate-100">
          {members.map((member) => (
            <div key={member.id} className="grid gap-3 px-5 py-4 text-sm md:grid-cols-[1fr_auto_auto] md:items-center">
              <div>
                <p className="font-medium text-slate-900">{member.email}</p>
                <p className="font-mono text-xs text-slate-500">{member.user_id}</p>
              </div>
              <span className="capitalize text-slate-500">{member.status}</span>
              <select value={member.role} onChange={(event) => void handleRole(member.id, event.target.value)} className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm capitalize">
                <option value="owner">Owner</option>
                <option value="admin">Admin</option>
                <option value="agent">Agent</option>
              </select>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleInvite} className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="font-display text-lg font-semibold">Invite teammate</h2>
        <label className="mt-5 block text-sm font-medium text-slate-700" htmlFor="invite-email">Email</label>
        <input id="invite-email" value={email} onChange={(event) => setEmail(event.target.value)} required type="email" className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900" />
        <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="invite-role">Role</label>
        <select id="invite-role" value={role} onChange={(event) => setRole(event.target.value)} className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">
          <option value="agent">Agent</option>
          <option value="admin">Admin</option>
        </select>
        <Button type="submit" variant="primary" className="mt-5 w-full">Invite</Button>
        {message ? <p className="mt-4 text-sm text-slate-600">{message}</p> : null}
      </form>
    </div>
  );
}