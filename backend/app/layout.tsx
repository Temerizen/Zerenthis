import type { Metadata } from "next";
import "./global.css";

export const metadata: Metadata = {
  title: "Zerenthis Admin",
  description:
    "Zerenthis admin shell for premium product, shorts, and YouTube pack generation.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
