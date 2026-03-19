import React, { useRef, useState } from "react";
import useStore from "../store.ts";

const ACCEPTED = [".txt", ".mp3", ".wav"];

const UploadForm = () => {
  const { setEarningsCalls, setLoading, setError, loading } = useStore();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const isValidFile = (file: File) =>
    ACCEPTED.some((ext) => file.name.toLowerCase().endsWith(ext));

  const handleFile = (file: File) => {
    if (!isValidFile(file)) {
      setError(`Unsupported file type. Please upload ${ACCEPTED.join(", ")}`);
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      setEarningsCalls(Array.isArray(data) ? data : [data]);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    }
  };

  return (
    <div>
      <h2>Upload Earnings Call</h2>
      <p>Upload a transcript or audio file to generate a summary.</p>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const file = e.dataTransfer.files[0];
          if (file) handleFile(file);
        }}
      >
        {selectedFile ? <p>{selectedFile.name}</p> : <p>Drag & drop a file here, or browse</p>}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED.join(",")}
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />

      <button onClick={handleSubmit} disabled={!selectedFile || loading}>
        {loading ? "Processing…" : "Upload & Analyze"}
      </button>
    </div>
  );
};

export default UploadForm;