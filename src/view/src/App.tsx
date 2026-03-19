import React from "react";
import useStore from "./store.ts";
import UploadForm from "./components/UploadForm.tsx";
import Dashboard from "./components/Dashboard.tsx";

export default function App() {
  const { earningsCalls, error }: { earningsCalls: any; error: string | null } = useStore();

  return (
    <div>
      {error && (
        <div>
          ⚠ {error}
        </div>
      )}
      {earningsCalls ? <Dashboard /> : <UploadForm />}
    </div>
  );
}