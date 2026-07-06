import Link from "next/link";

import { UrgencyRail } from "@/components/ui/Badges";
import { TicketPriorityBadge } from "./TicketPriorityBadge";
import { TicketStatusBadge } from "./TicketStatusBadge";
import type { TicketListItem } from "../types";

export function TicketList({ tickets }: { tickets: TicketListItem[] }) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8">
        <h2 className="font-display text-lg font-semibold">Nothing waiting on you</h2>
        <p className="mt-2 text-sm text-slate-600">The active queue is clear. Check back after the next Gmail import or triage run.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="hidden md:block">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="w-3 px-0 py-3" />
              <th className="px-4 py-3">Subject</th>
              <th className="px-4 py-3">Sender</th>
              <th className="px-4 py-3">Urgency</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">AI confidence</th>
              <th className="px-4 py-3">Received</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {tickets.map((ticket) => (
              <tr key={ticket.id} className="hover:bg-slate-50">
                <td className="px-0 py-0 align-stretch"><UrgencyRail priority={ticket.priority} className="h-full min-h-14 rounded-none" /></td>
                <td className="px-4 py-3 font-medium text-slate-900"><Link href={`/dashboard/tickets/${ticket.id}`}>{ticket.subject}</Link></td>
                <td className="px-4 py-3 text-slate-600">{ticket.customer_name ?? ticket.customer_email}</td>
                <td className="px-4 py-3"><TicketPriorityBadge priority={ticket.priority} /></td>
                <td className="px-4 py-3 text-slate-600">{ticket.category.replaceAll("_", " ")}</td>
                <td className="px-4 py-3"><TicketStatusBadge status={ticket.status} /></td>
                <td className="px-4 py-3 font-mono text-xs text-slate-500">N/A</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-500">{new Date(ticket.received_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="divide-y divide-slate-100 md:hidden">
        {tickets.map((ticket) => (
          <Link key={ticket.id} href={`/dashboard/tickets/${ticket.id}`} className="grid grid-cols-[auto_1fr] gap-3 p-4">
            <UrgencyRail priority={ticket.priority} className="h-full" />
            <div>
              <p className="font-medium text-slate-900">{ticket.subject}</p>
              <p className="mt-1 text-sm text-slate-500">{ticket.customer_name ?? ticket.customer_email}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <TicketPriorityBadge priority={ticket.priority} />
                <TicketStatusBadge status={ticket.status} />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}