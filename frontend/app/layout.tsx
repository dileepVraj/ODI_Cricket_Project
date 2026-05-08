import type { Metadata } from "next";
import "./globals.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/cards.css";
import "./styles/inputs.css";
import "./styles/data.css";
import "./styles/landing.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Vantage | Strategic Algo Exchange",
  description:
    "AI-powered cricket analysis for algo-trading. " +
    "Venue intelligence, rivalry analysis, score prediction, and match-day packs.",
  icons: {
    icon: "/icon.png",
  },
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
