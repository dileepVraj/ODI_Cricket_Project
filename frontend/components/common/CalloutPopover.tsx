"use client";

import { useState, useRef, useEffect } from "react";

interface CalloutPopoverProps {
  number: number;
  title: string;
  description: string;
}

type TooltipPos = {
  above: boolean;
  buttonTop: number;
  buttonBottom: number;
  tooltipLeft: number;
  viewportHeight: number;
};

const TOOLTIP_W = 256; // w-64

export default function CalloutPopover({ number, title, description }: CalloutPopoverProps) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<TooltipPos | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const rawLeft = rect.left + rect.width / 2 - TOOLTIP_W / 2;
      const clampedLeft = Math.max(8, Math.min(rawLeft, window.innerWidth - TOOLTIP_W - 8));
      setPos({
        above: rect.top > 160,
        buttonTop: rect.top,
        buttonBottom: rect.bottom,
        tooltipLeft: clampedLeft,
        viewportHeight: window.innerHeight,
      });
    }
    function onMouseDown(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onMouseDown);
    return () => document.removeEventListener("mousedown", onMouseDown);
  }, [open]);

  const badgeStyle: React.CSSProperties = {
    background: "var(--callout-badge-bg)",
    color: "var(--callout-badge-text)",
    boxShadow: "var(--callout-badge-glow)",
  };

  const tooltipStyle: React.CSSProperties = pos
    ? {
        position: "fixed",
        left: pos.tooltipLeft,
        zIndex: 9999,
        ...(pos.above
          ? { bottom: pos.viewportHeight - pos.buttonTop + 8 }
          : { top: pos.buttonBottom + 8 }),
      }
    : { display: "none" };

  return (
    <div ref={containerRef} className="relative inline-flex">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={`Callout ${number}: ${title}`}
        className="w-5 h-5 rounded-full flex items-center justify-center font-data text-[10px] font-black cursor-pointer select-none shrink-0 transition-transform hover:scale-110"
        style={badgeStyle}
      >
        {number}
      </button>
      {open && pos && (
        <div
          role="tooltip"
          style={tooltipStyle}
          className="w-64 [background:var(--bg-elevated)] [border:1px_solid_var(--border-strong)] [border-radius:8px] p-4 [box-shadow:var(--shadow-lg)] font-sans [text-transform:none] [letter-spacing:normal] text-left"
        >
          <div className="[border-left:3px_solid_var(--accent-ui)] pl-3">
            <p className="[font-size:13px] font-bold font-sans [color:var(--text-primary)] mb-1">{title}</p>
            <p className="[font-size:12px] font-normal font-sans [color:var(--text-secondary)] [line-height:1.6]">{description}</p>
          </div>
        </div>
      )}
    </div>
  );
}
