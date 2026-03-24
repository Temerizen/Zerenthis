import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zerenthis",
  description:
    "Zerenthis is an intelligent creation engine for premium documents, short-form content, YouTube scripts, and guided AI production workflows.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}