import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CricketAlgo — Trading Intelligence Platform",
  description:
    "AI-powered cricket analysis for algo-trading. " +
    "Venue intelligence, rivalry analysis, score prediction, and match-day packs.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
