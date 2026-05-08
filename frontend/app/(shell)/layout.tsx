import { AppProvider } from "@/lib/context";
import { CockpitTradeDraftProvider } from "@/lib/cockpit/CockpitTradeDraftContext";
import TopBar from "@/components/layout/TopBar";
import Sidebar from "@/components/layout/Sidebar";
import ShellContextBar from "@/components/layout/ShellContextBar";

export const dynamic = "force-dynamic";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppProvider>
      <CockpitTradeDraftProvider>
        <TopBar />
        <div className="app-shell">
          <Sidebar />
          <div className="app-main">
            <ShellContextBar />
            <main className="app-content">
              {children}
            </main>
          </div>
        </div>
      </CockpitTradeDraftProvider>
    </AppProvider>
  );
}
