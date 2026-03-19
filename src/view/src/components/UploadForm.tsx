import React, { useRef, useState, useEffect } from "react";
import useStore from "../store";

const ACCEPTED = [".txt", ".mp3", ".wav"];

interface UploadFormProps {
  onLoadMock?: () => void;
}

const UploadForm = ({ onLoadMock }: UploadFormProps) => {
  const { setEarningsCalls, setLoading, setError, loading } = useStore();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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
    <div className="min-h-screen bg-brand-bg flex items-center justify-center p-6">
      <div className="w-full max-w-lg bg-brand-card border border-brand-border rounded-card p-8">

        {/* Header row with three-dot menu */}
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="font-sans text-xl font-semibold text-brand-text mb-1">
              Upload Earnings Call
            </h2>
            <p className="font-sans text-sm text-brand-subtext">
              Upload a transcript or audio file to generate a summary.
            </p>
          </div>

          {/* Three-dot menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((prev) => !prev)}
              className="p-1.5 rounded-md text-brand-muted hover:text-brand-text hover:bg-brand-border/50 transition-colors"
              aria-label="More options"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <circle cx="8" cy="2.5" r="1.5" />
                <circle cx="8" cy="8" r="1.5" />
                <circle cx="8" cy="13.5" r="1.5" />
              </svg>
            </button>

            {menuOpen && (
              <div className="absolute right-0 mt-1 w-44 bg-brand-card border border-brand-border rounded-card shadow-card z-20 py-1 overflow-hidden">
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    onLoadMock?.();
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-brand-text hover:bg-brand-border/40 transition-colors"
                >
                  Try for Free!
                </button>
              </div>
            )}
          </div>
        </div>

        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
          }}
          className={`
            cursor-pointer rounded-card border-2 border-dashed p-10
            flex flex-col items-center justify-center gap-2
            transition-colors duration-150
            ${dragging
              ? "border-brand-accent bg-brand-accent/10"
              : selectedFile
              ? "border-brand-accent bg-brand-accent/5"
              : "border-brand-border hover:border-brand-muted"
            }
          `}
        >
          {selectedFile ? (
            <>
              <p className="text-xs text-brand-subtext uppercase tracking-widest">File Loaded</p>
              <p className="text-sm text-brand-accent font-medium">{selectedFile.name}</p>
              <p className="text-xs text-brand-muted">Click to replace</p>
            </>
          ) : (
            <>
              <p className="text-sm text-brand-text font-medium">Drag & drop a file here, or browse</p>
              <p className="text-xs text-brand-subtext">
                {ACCEPTED.map(e => e.replace(".", "").toUpperCase()).join("  ·  ")}
              </p>
            </>
          )}
        </div>

        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(",")}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />

        <button
          onClick={handleSubmit}
          disabled={!selectedFile || loading}
          className={`
            mt-4 w-full py-3 rounded-card text-sm font-semibold
            transition-all duration-150
            ${!selectedFile || loading
              ? "bg-brand-border text-brand-muted cursor-not-allowed"
              : "bg-brand-accent text-brand-bg hover:brightness-110 active:scale-95 cursor-pointer"
            }
          `}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>

      </div>
    </div>
  );
};

export default UploadForm;