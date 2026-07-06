import { LoginForm } from "@/features/auth/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-slate-950">
      <section className="mx-auto max-w-5xl">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Sign in</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">Access Support Triage</h1>
        <p className="mt-4 max-w-2xl text-slate-600">
          Sign in with Supabase Auth so the frontend can call FastAPI with your bearer token.
        </p>
        <LoginForm />
      </section>
    </main>
  );
}
