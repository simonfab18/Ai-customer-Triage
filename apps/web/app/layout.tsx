import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Support Triage",
  description: "AI-assisted customer support triage and response approval.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

