import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-black text-white">
        <div className="flex">
          <aside className="w-64 h-screen bg-[#05070d] border-r border-cyan-500 p-4">
            <h1 className="text-xl font-bold text-cyan-400 mb-6">Zerenthis</h1>
            <nav className="space-y-3 text-sm">
              <a href="/" className="block hover:text-cyan-300">Home</a>
              <a href="/dashboard" className="block hover:text-cyan-300">Dashboard</a>
              <a href="/cosmic-map" className="block hover:text-cyan-300">Cosmic Map</a>
              <a href="/systems" className="block hover:text-cyan-300">Systems</a>
              <a href="/money" className="block hover:text-cyan-300">Money Engine</a>
              <a href="/traffic" className="block hover:text-cyan-300">Traffic</a>
              <a href="/leaderboard" className="block hover:text-cyan-300">Leaderboard</a>
              <a href="/lab" className="block hover:text-cyan-300">Lab</a>
              <a href="/roadmap" className="block hover:text-cyan-300">Roadmap</a>
            </nav>
          </aside>

          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
