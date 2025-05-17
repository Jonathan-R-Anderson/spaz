import { useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";

type Props = {
  targetPath: string;
};

const queryClient = new QueryClient();

const App = ({ targetPath }: Props) => {
  useEffect(() => {
    const app = "loading"; // 👈 FORCE use of 'loading' as the only app

    console.log("Target path:", targetPath);
    console.log("Using app:", app);

    fetch(`/load_app/${app}`).then(() => {
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

      const interval = setInterval(async () => {
        const ready = await checkAssets();
        if (ready) {
          clearInterval(interval);
          window.location.href = `/static/apps/${app}${targetPath}`;
        }
      }, 1500);
    });
  }, [targetPath]);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <div className="loader-screen">
          <h1>Loading your experience…</h1>
          <p>Fetching content securely via decentralized web...</p>
        </div>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
