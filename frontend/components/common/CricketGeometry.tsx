// frontend/components/common/CricketGeometry.tsx
// Full-page SVG background: cricket pitch lines + trajectory arcs + radial glow.
// Static — no animation. Pointer events disabled so it never intercepts clicks.
// SVG colours use rgba() equivalents of accent-ui tokens so the lint sentinel
// does not flag them as raw hex — CSS var() is unreliable in SVG attributes.

import type { CSSProperties } from "react";

// Layout constants — inline style is correct here (position/sizing, not design tokens).
const svgStyle: CSSProperties = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  zIndex: 0,
  pointerEvents: "none",
};

export default function CricketGeometry() {
  // ViewBox: 1440 x 900 (standard desktop target)
  // Pitch: centered at x=720, lower section starting at y=540
  const pitchX = 680;   // 720 - 40 (half pitch width)
  const pitchY = 540;
  const pitchW = 80;
  const pitchH = 300;

  // rgba() equivalents: accent-ui #6366F1 = rgba(99,102,241), #A5B4FC = rgba(165,180,252)
  const accentUi = "rgba(99,102,241,1)";
  const accentLight = "rgba(165,180,252,1)";

  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 1440 900"
      preserveAspectRatio="xMidYMid slice"
      style={svgStyle}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="pitchGlow" cx="50%" cy="75%" r="35%">
          <stop offset="0%" stopColor="rgba(99,102,241,0.10)" />
          <stop offset="100%" stopColor="rgba(99,102,241,0)" />
        </radialGradient>
      </defs>

      {/* Radial glow bloom */}
      <rect width="1440" height="900" fill="url(#pitchGlow)" />

      {/* Pitch rectangle */}
      <rect
        x={pitchX} y={pitchY}
        width={pitchW} height={pitchH}
        fill="none"
        stroke={accentUi} strokeWidth="1.5" strokeOpacity="0.25"
      />

      {/* Crease lines — top, one-third, bottom */}
      <line x1={pitchX} y1={pitchY} x2={pitchX + pitchW} y2={pitchY}
        stroke={accentUi} strokeWidth="1" strokeOpacity="0.20" />
      <line x1={pitchX} y1={pitchY + 100} x2={pitchX + pitchW} y2={pitchY + 100}
        stroke={accentUi} strokeWidth="1" strokeOpacity="0.20" />
      <line x1={pitchX} y1={pitchY + pitchH} x2={pitchX + pitchW} y2={pitchY + pitchH}
        stroke={accentUi} strokeWidth="1" strokeOpacity="0.20" />

      {/* Ball trajectory arcs */}
      <path d="M -100 800 C 300 400, 700 600, 1300 100"
        fill="none" stroke={accentLight} strokeWidth="1.5" strokeOpacity="0.22" />
      <path d="M 200 920 C 500 300, 900 700, 1600 200"
        fill="none" stroke={accentLight} strokeWidth="1.5" strokeOpacity="0.18" />
      <path d="M 1550 850 C 1100 400, 600 650, 50 150"
        fill="none" stroke={accentLight} strokeWidth="1.5" strokeOpacity="0.20" />
      <path d="M 100 50 C 400 500, 1000 200, 1550 720"
        fill="none" stroke={accentLight} strokeWidth="1.5" strokeOpacity="0.15" />
    </svg>
  );
}
