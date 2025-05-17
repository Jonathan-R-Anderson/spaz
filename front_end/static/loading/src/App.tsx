import { useEffect, useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";

const queryClient = new QueryClient();

const App = () => {
  const [loading, setLoading] = useState(true);
  const [targetPath, setTargetPath] = useState("/");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const target = params.get("target") || "/";
    setTargetPath(target);

    const app = "loading"; // 🔒 hardcoded for now

    const checkAssets = async () => {
      const indexUrl = `/static/apps/${app}/index.html`;
      const res = await fetch(indexUrl);
      if (!res.ok) return false;

      const html = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");

      const assetUrls: string[] = [];

      doc.querySelectorAll("script[src]").forEach((el) => {
        const src = el.getAttribute("src");
        if (src) assetUrls.push(src);
      });

      doc.querySelectorAll("link[rel='stylesheet'][href]").forEach((el) => {
        const href = el.getAttribute("href");
        if (href) assetUrls.push(href);
      });

      const checks = await Promise.all(
        assetUrls.map((url) =>
          fetch(url, { method: "HEAD" }).then((r) => r.ok).catch(() => false)
        )
      );

      return checks.every(Boolean);
    };

    fetch(`/load_app/${app}`).then(() => {
      const interval = setInterval(async () => {
        const ready = await checkAssets();
        if (ready) {
          clearInterval(interval);
          // ✅ Now stay in place — no redirect
          setLoading(false);
        }
      }, 1500);
    });
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        {loading ? (
          <div className="loader-screen">
            <h1>Loading your experience…</h1>
            <p>Fetching content securely via decentralized web...</p>
          </div>
        ) : (
          <div className="loaded-content">
            <h1>✅ Loaded: {targetPath}</h1>
            <p>This is where you mount or route to the actual app.</p>
          </div>
        )}
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
