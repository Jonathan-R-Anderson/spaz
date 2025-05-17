import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

const target = new URLSearchParams(window.location.search).get('target') || '/';

createRoot(document.getElementById("root")!).render(
  <App targetPath={target} />
);
