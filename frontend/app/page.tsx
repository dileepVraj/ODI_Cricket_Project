/**
 * app/page.tsx - Main Application Shell
 *
 * Composes the 3-layer layout:
 *   Layer 1: FormatSelector (top)
 *   Layer 2: ContextBar (below top)
 *   Layer 3: Sidebar (left) + Main Content (right)
 *
 * Renders CategoryScreen for the active manifest category.
 */
"use client";

import { useEffect, useState } from "react";
import { useAppContext } from "@/lib/context";
import ContextBar from "@/components/layout/ContextBar";
import FormatSelector from "@/components/layout/FormatSelector";
import Sidebar from "@/components/layout/Sidebar";
import { CategoryScreen } from "@/components/layout/CategoryScreen";

const NAV_ROOT_FALLBACK = "dashboard";

export default function Page() {
  return <AppShell />;
}

function AppShell() {
  const { manifest } = useAppContext();
  const navRootKey = manifest?.navigation_root?.key ?? NAV_ROOT_FALLBACK;

  const [activeCategory, setActiveCategory] = useState(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      if (hash) return hash;
    }
    return navRootKey;
  });

  useEffect(() => {
    function onHashChange() {
      const hash = window.location.hash.replace("#", "");
      if (hash) setActiveCategory(hash);
      else setActiveCategory(navRootKey);
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, [navRootKey]);

  useEffect(() => {
    if (manifest && activeCategory === navRootKey && manifest.categories.length > 0) {
      const firstCategory = manifest.categories[0].key;
      setActiveCategory(firstCategory);
      window.history.replaceState(null, "", `#${firstCategory}`);
    }
  }, [manifest, navRootKey]);

  const handleCategorySelect = (cat: string) => {
    setActiveCategory(cat);
    if (cat === navRootKey) {
      window.history.replaceState(null, "", window.location.pathname);
    } else {
      window.history.replaceState(null, "", `#${cat}`);
    }
  };

  return (
    <div
      className="[display:flex] [flex-direction:column] [height:100vh] [overflow:hidden]"
    >
      <FormatSelector />
      <ContextBar />
      <div className="[display:flex] [flex:1] [overflow:hidden]">
        <Sidebar
          activeCategory={activeCategory}
          onCategorySelect={handleCategorySelect}
        />
        <main
          id="main-content"
          className="[flex:1] [overflow:auto] [padding:24px] [background:var(--bg-deepest)]"
        >
          <CategoryScreen categoryKey={activeCategory} />
        </main>
      </div>
    </div>
  );
}
