import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// ✅ Extract `target` from query string
const params = new URLSearchParams(window.location.search);
const target = params.get("target") || "/";

// ✅ Replace current browser URL with the intended path *before* rendering
if (window.location.pathname === "/loading") {
  window.history.replaceState({}, "", target);
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App targetPath={target} />
  </React.StrictMode>
);
