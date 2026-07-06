import { cx } from "./cx";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "outline" | "ghost" | "danger";
};

const variants = {
  primary: "bg-brand-600 text-white hover:bg-brand-700 disabled:bg-slate-300",
  outline: "border border-slate-300 bg-white text-slate-700 hover:border-slate-400 disabled:text-slate-400",
  ghost: "text-slate-600 hover:bg-slate-100 disabled:text-slate-400",
  danger: "border border-rose-200 bg-white text-rose-700 hover:bg-rose-50 disabled:text-slate-400",
};

export function Button({ className, variant = "outline", ...props }: ButtonProps) {
  return (
    <button
      {...props}
      className={cx(
        "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed",
        variants[variant],
        className,
      )}
    />
  );
}