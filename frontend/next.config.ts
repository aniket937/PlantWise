import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Wikimedia serves the same file from both hosts; both are allowed so a
    // response from either the API or the image optimiser resolves.
    remotePatterns: [
      { protocol: "https", hostname: "upload.wikimedia.org", pathname: "/**" },
      { protocol: "https", hostname: "thumb.wikimedia.org", pathname: "/**" },
    ],
    formats: ["image/webp"],
  },
  poweredByHeader: false,
};

export default nextConfig;
