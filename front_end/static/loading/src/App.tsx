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
    // Step 1: Determine app name based on path
    let app = "welcome";
    if (targetPath.startsWith("/dashboard")) app = "dashboard";
    else if (targetPath.startsWith("/users")) app = "profile";

    // Step 2: Ask backend to fetch/verify availability
    fetch(`/load_app/${app}`).then(() => {
      const interval = setInterval(() => {
        fetch(`/static/apps/${app}/index.html`, { method: "HEAD" }).then(res => {
          if (res.ok) {
            clearInterval(interval);

            // ✅ Redirect to FULL path within the loaded app
            window.location.href = `/static/apps/${app}${targetPath}`;
          }
        });
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
