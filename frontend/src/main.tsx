import React from "react";
import ReactDOM from "react-dom/client";

const App = () => (
  <main>
    <h1>Richwell Portal</h1>
    <p>Frontend bootstrapped for Phase 0.</p>
  </main>
);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
