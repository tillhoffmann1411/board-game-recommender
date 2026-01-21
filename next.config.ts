import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cf.geekdo-images.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "s3-us-west-1.amazonaws.com",
        pathname: "/5cc.images/**",
      },
    ],
    // Configure allowed image qualities (required in Next.js 16+)
    qualities: [50, 70, 75, 85, 100],
    // Enable AVIF format for better compression (with WebP fallback)
    formats: ["image/avif", "image/webp"],
    // Optimize device sizes for card grids
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    // Smaller sizes for card thumbnails
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

export default nextConfig;
