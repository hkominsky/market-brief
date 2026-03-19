import React, { useState, useRef, useEffect } from "react";

type Message = { role: "user" | "assistant"; content: string };

const QAChat = ({ transcript }: { transcript: string }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const updated: Message[] = [...messages, { role: "user", content: question }];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript, question, history: messages }),
      });
      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();
      setMessages([...updated, { role: "assistant", content: data.answer }]);
    } catch {
      setMessages([...updated, { role: "assistant", content: "Something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-brand-card border border-brand-border rounded-card p-8">
      <p className="text-md font-semibold text-brand-text mb-4">Ask a Question</p>

      {messages.length > 0 && (
        <div className="flex flex-col gap-3 mb-4 max-h-72 overflow-y-auto">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`text-sm px-4 py-2.5 rounded-card max-w-[85%] leading-relaxed ${
                m.role === "user"
                  ? "bg-brand-accent text-brand-bg self-end"
                  : "bg-brand-bg border border-brand-border text-brand-text self-start"
              }`}
            >
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="text-sm px-4 py-2.5 rounded-card bg-brand-bg border border-brand-border text-brand-muted self-start animate-pulse-soft">
              Thinking...
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="e.g. What was the revenue growth YoY?"
          className="flex-1 bg-brand-bg border border-brand-border rounded-card px-4 py-2.5 text-sm text-brand-text placeholder:text-brand-muted focus:outline-none focus:border-brand-accent transition-colors duration-150"
        />
        <button
          onClick={send}
          disabled={!input.trim() || loading}
          className={`
            px-4 py-2.5 rounded-card text-sm font-semibold transition-all duration-150
            ${!input.trim() || loading
              ? "bg-brand-border text-brand-muted cursor-not-allowed"
              : "bg-brand-accent text-brand-bg hover:brightness-110 active:scale-95 cursor-pointer"
            }
          `}
        >
          Ask
        </button>
      </div>
    </div>
  );
};

export default QAChat;