import Link from "next/link";

const settings = [
  { href: "/dashboard/settings", label: "Integrations", description: "Gmail connection and import controls" },
  { href: "/dashboard/settings/team", label: "Team", description: "Invite teammates and manage roles" },
  { href: "/dashboard/settings/workspace", label: "Workspace", description: "Name, signature, and preferences" },
];

export function SettingsNav() {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {settings.map((item) => (
        <Link key={item.href} href={item.href} className="rounded-lg border border-slate-200 bg-white p-4 hover:border-slate-300">
          <p className="font-display text-lg font-semibold text-slate-900">{item.label}</p>
          <p className="mt-1 text-sm text-slate-500">{item.description}</p>
        </Link>
      ))}
    </div>
  );
}