import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#9333ea" },
    { media: "(prefers-color-scheme: dark)", color: "#9333ea" },
  ],
};

export const metadata: Metadata = {
  title: {
    default: "Board Game Recommender",
    template: "%s | Board Game Recommender",
  },
  description: "Discover your next favorite board game with personalized recommendations powered by smart algorithms. Rate games you've played and get tailored suggestions from 20,000+ board games.",
  keywords: ["board games", "game recommendations", "board game reviews", "personalized recommendations", "game ratings", "board game catalog"],
  authors: [{ name: "Board Game Recommender" }],
  creator: "Board Game Recommender",
  publisher: "Board Game Recommender",
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    siteName: "Board Game Recommender",
    title: "Board Game Recommender - Discover Your Next Favorite Game",
    description: "Discover your next favorite board game with personalized recommendations powered by smart algorithms. Rate games you've played and get tailored suggestions from 20,000+ board games.",
    images: [
      {
        url: "/boreg-icon.png",
        width: 1200,
        height: 1200,
        alt: "Board Game Recommender - Discover Your Next Favorite Game",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Board Game Recommender - Discover Your Next Favorite Game",
    description: "Discover your next favorite board game with personalized recommendations powered by smart algorithms.",
    images: ["/boreg-icon.png"],
    creator: "@boardgamerec",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/favicon_io/favicon.ico", sizes: "any" },
      { url: "/favicon_io/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon_io/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [
      { url: "/favicon_io/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  manifest: "/manifest.json",
  category: "entertainment",
};

// Force dynamic rendering for entire app (uses Clerk auth)
export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider dynamic>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>{children}</body>
      </html>
    </ClerkProvider>
  );
}
