import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    lockDistDir: false,
    workerThreads: true,
  },

  turbopack: {
    root: process.cwd(),
  },

  // Move Next.js dev indicator away from the left sidebar area.
  devIndicators: {
    position: "bottom-right",
  },

  // Proxy API requests to FastAPI backend during development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/health",
        destination: "http://127.0.0.1:8000/health",
      },
    ];
  },
};

export default nextConfig;
