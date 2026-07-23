import type { NextConfig } from "next";

const backendApiBase =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendApiBase}/:path*`,
      },
    ];
  },
};

export default nextConfig;
