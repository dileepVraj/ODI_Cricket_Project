import type { Metadata } from "next";
import { Suspense } from "react";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppProvider } from "@/lib/context";
import TopBar from "@/components/layout/TopBar";
import Sidebar from "@/components/layout/Sidebar";
import ContextBar from "@/components/layout/ContextBar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <AppProvider>
          <TopBar />
          <div className="app-shell">
            <Sidebar />
            <div className="app-main">
              <Suspense fallback={<div className="context-bar" aria-hidden="true" />}>
                <ContextBar />
              </Suspense>
              <main className="app-content">
                {children}
              </main>
            </div>
          </div>
        </AppProvider>
      </body>
    </html>
  );
}
