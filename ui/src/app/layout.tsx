import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HART-Morphosis",
  description: "Nature-inspired enterprise image generation — grow images from rules.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
