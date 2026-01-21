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
  },
};

export default nextConfig;
