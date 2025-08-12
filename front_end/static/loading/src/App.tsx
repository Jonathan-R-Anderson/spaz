import { useEffect, useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import "./index.css";
import LoadingPage from "./components/LoadingPage";

const queryClient = new QueryClient();

interface AppProps {
  targetPath: string;
}

const App: React.FC<AppProps> = ({ targetPath }) => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const app = "loading";

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
          <div className="loader-screen" />
        ) : (
          <BrowserRouter basename="/static/apps/loading/">
            <Routes>
              <Route path="/" element={<Index targetPath={targetPath} />} />
              <Route
                path="/users/:eth_address"
                element={<LoadingPage onComplete={() => setLoading(false)} />}
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        )}
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
