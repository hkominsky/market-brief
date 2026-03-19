import React, { useEffect } from "react";
import useStore from "./store";
import UploadForm from "./components/UploadForm";
import Dashboard from "./components/Dashboard";

export default function App() {
  const { earningsCalls, error, setError } = useStore();

  useEffect(() => {
    if (error) {
      const t = setTimeout(() => setError(""), 4000);
      return () => clearTimeout(t);
    }
  }, [error]);

  return (
    <div>
      {error && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-3 bg-brand-card border border-brand-negative/30 text-brand-text text-sm px-4 py-3 rounded-card shadow-card max-w-sm">
          <span className="text-brand-negative text-base">⚠</span>
          <span>{error}</span>
        </div>
      )}
      {earningsCalls ? <Dashboard /> : <UploadForm />}
    </div>
  );
}