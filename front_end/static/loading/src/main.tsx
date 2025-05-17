import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const params = new URLSearchParams(window.location.search);
const target = params.get("target") || "/";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App targetPath={target} />
  </React.StrictMode>
);
