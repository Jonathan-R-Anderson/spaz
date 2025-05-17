import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { BrowserRouter } from "react-router-dom";

const target = new URLSearchParams(window.location.search).get('target') || '/';

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename="/static/apps/loading/">
      <App targetPath={target} />
    </BrowserRouter>
  </React.StrictMode>
);
