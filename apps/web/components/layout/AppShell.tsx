"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { getStoredOrganizationId } from "@/features/organizations/components/OrganizationManager";
import { getMe } from "@/lib/api-client";
import type { Organization } from "@/lib/api-types";
import { createClient } from "@/lib/supabase/client";
import { getMetricsOverview } from "@/features/tickets/api";
import type { MetricsOverview } from "@/features/tickets/types";
import { cx } from "@/components/ui/cx";

const navItems = [
  { href: "/dashboard", label: "Dashboard", mark: "D" },
  { href: "/dashboard/tickets", label: "Triage queue", mark: "Q", badge: "pending" },
  { href: "/dashboard/settings", label: "Settings", mark: "S", ownerOnly: true },
];

function pageTitle(pathname: string) {
  if (pathname.includes("/tickets/")) return "Ticket detail";
  if (pathname.includes("/tickets")) return "Triage queue";
  if (pathname.includes("/settings/team")) return "Team";
  if (pathname.includes("/settings/workspace")) return "Workspace";
  if (pathname.includes("/settings")) return "Settings";
  if (pathname.includes("/organizations")) return "Organizations";
  return "Dashboard";
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const supabase = createClient();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null);

  useEffect(() => {
    async function loadContext() {
      const { data } = await supabase.auth.getSession();
      const accessToken = data.session?.access_token;
      if (!accessToken) return;
      const me = await getMe(accessToken);
      const stored = getStoredOrganizationId();
      const selected = me.organizations.find((item) => item.id === stored) ?? me.organizations[0] ?? null;
      setOrganization(selected);
      if (selected) {
        try {
          setMetrics(await getMetricsOverview(selected.id, accessToken));
        } catch {
          setMetrics(null);
        }
      }
    }
    void loadContext();
  }, [pathname, supabase]);

  const role = organization?.role ?? "agent";
  const canSeeOwnerSettings = role === "owner" || role === "admin";
  const pendingCount = metrics?.active_tickets ?? 0;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 md:pl-64">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-200 bg-white md:flex md:flex-col">
        <div className="border-b border-slate-200 px-5 py-5">
          <Link href="/dashboard" className="font-display text-xl font-semibold tracking-tight text-slate-900">
            TriageLab
          </Link>
          <p className="mt-1 text-xs text-slate-500">AI support command center</p>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems
            .filter((item) => !item.ownerOnly || canSeeOwnerSettings)
            .map((item) => {
              const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cx(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                    active ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                  )}
                >
                  <span className={cx("grid h-7 w-7 place-items-center rounded-md border text-xs font-display", active ? "border-white/20 bg-white/10" : "border-slate-200 bg-white")}>{item.mark}</span>
                  <span className="flex-1">{item.label}</span>
                  {item.badge && pendingCount > 0 ? (
                    <span className={cx("rounded-full px-2 py-0.5 font-mono text-xs", active ? "bg-white text-slate-900" : "bg-teal-50 text-teal-700")}>{pendingCount}</span>
                  ) : null}
                </Link>
              );
            })}
        </nav>
        <div className="border-t border-slate-200 p-4 text-sm">
          <p className="font-medium text-slate-900">{organization?.name ?? "No workspace selected"}</p>
          <p className="mt-1 capitalize text-slate-500">{organization?.role ?? "Select an organization"}</p>
          <Link href="/dashboard/organizations" className="mt-3 inline-flex text-xs font-medium text-teal-700">
            Change workspace
          </Link>
        </div>
      </aside>

      <div className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-3 border-t border-slate-200 bg-white md:hidden">
        {navItems
          .filter((item) => !item.ownerOnly || canSeeOwnerSettings)
          .map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link key={item.href} href={item.href} className={cx("relative py-3 text-center text-xs font-medium", active ? "text-slate-900" : "text-slate-500")}>
                <span className="block font-display text-sm">{item.mark}</span>
                {item.label}
                {item.badge && pendingCount > 0 ? <span className="absolute right-5 top-2 rounded-full bg-teal-600 px-1.5 text-[10px] text-white">{pendingCount}</span> : null}
              </Link>
            );
          })}
      </div>

      <header className="sticky top-0 z-20 border-b border-slate-200 bg-slate-50/95 px-5 py-4 backdrop-blur md:px-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="font-mono text-xs text-slate-500">{organization?.slug ?? "workspace"}</p>
            <h1 className="font-display text-2xl font-semibold tracking-tight text-slate-900">{pageTitle(pathname)}</h1>
          </div>
          <Link href="/login" className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700">
            Account
          </Link>
        </div>
      </header>

      <main className="px-5 py-6 pb-24 md:px-8 md:pb-8">{children}</main>
    </div>
  );
}