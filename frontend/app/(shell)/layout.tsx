import { Suspense } from "react";
import { AppProvider } from "@/lib/context";
import TopBar from "@/components/layout/TopBar";
import Sidebar from "@/components/layout/Sidebar";
import ContextBar from "@/components/layout/ContextBar";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
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
  );
}
