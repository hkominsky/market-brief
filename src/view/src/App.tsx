import React from "react";
import useStore from "./store";
import UploadForm from "./components/UploadForm";
import Dashboard from "./components/Dashboard";

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