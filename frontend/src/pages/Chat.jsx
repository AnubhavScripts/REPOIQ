import { useState } from "react";
import { chat, reviewRepo } from "../services/api";
import { useLocation } from "react-router-dom";

const SCORE_COLOR = (s) => {
  if (s >= 8) return "#22c55e";
  if (s >= 5) return "#f59e0b";
  return "#ef4444";
};

function ScoreBadge({ score }) {
  return (
    <span
      style={{
        color: SCORE_COLOR(score),
        fontWeight: 700,
        fontSize: "1.1rem",
      }}
    >
      {score}/10
    </span>
  );
}

function IssueCard({ issue }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      style={{
        background: "#1a1a2e",
        border: "1px solid #ef444444",
        borderRadius: 8,
        marginBottom: 8,
        overflow: "hidden",
      }}
    >
      <button
        onClick={() => setOpen((p) => !p)}
        style={{
          width: "100%",
          textAlign: "left",
          background: "none",
          border: "none",
          color: "#fca5a5",
          fontWeight: 600,
          padding: "10px 14px",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        ⚠ {issue.issue}
        <span style={{ color: "#6b7280" }}>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div style={{ padding: "0 14px 12px", color: "#d1d5db", fontSize: "0.85rem", lineHeight: 1.6 }}>
          <p><span style={{ color: "#9ca3af" }}>Evidence:</span> {issue.evidence}</p>
          <p><span style={{ color: "#9ca3af" }}>Impact:</span> {issue.impact}</p>
          <p><span style={{ color: "#9ca3af" }}>Fix:</span> {issue.recommendation}</p>
          {issue.example_fix && (
            <pre style={{
              background: "#0f0f1a",
              borderRadius: 6,
              padding: "6px 10px",
              marginTop: 6,
              overflowX: "auto",
              color: "#86efac",
              fontSize: "0.8rem",
            }}>{issue.example_fix}</pre>
          )}
        </div>
      )}
    </div>
  );
}

function AgentSection({ title, emoji, data }) {
  if (!data) return null;
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <span style={{ fontSize: "1.3rem" }}>{emoji}</span>
        <h3 style={{ color: "#e5e7eb", margin: 0, fontSize: "1rem", fontWeight: 700 }}>{title}</h3>
        <ScoreBadge score={data.score} />
      </div>
      {data.issues?.length === 0 ? (
        <p style={{ color: "#22c55e", fontSize: "0.85rem" }}>✅ No issues found.</p>
      ) : (
        data.issues?.map((iss, i) => <IssueCard key={i} issue={iss} />)
      )}
    </div>
  );
}

function ReviewPanel({ report, onClose }) {
  return (
    <div style={{
      position: "fixed", inset: 0, background: "#00000099",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 50, padding: 20,
    }}>
      <div style={{
        background: "#0d0d1a",
        border: "1px solid #374151",
        borderRadius: 12,
        width: "100%",
        maxWidth: 720,
        maxHeight: "90vh",
        overflowY: "auto",
        padding: 28,
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <div>
            <h2 style={{ color: "#f87171", margin: 0, fontSize: "1.4rem" }}>🔥 Brutal Code Review</h2>
            <p style={{ color: "#6b7280", margin: "4px 0 0", fontSize: "0.85rem" }}>
              Overall Score: <ScoreBadge score={report.overall_score} />
            </p>
          </div>
          <button onClick={onClose} style={{
            background: "#1f2937", border: "none", color: "#9ca3af",
            borderRadius: 6, padding: "6px 12px", cursor: "pointer",
          }}>✕ Close</button>
        </div>

        {/* Verdict */}
        <div style={{
          background: "#1a1a2e", border: "1px solid #7c3aed44",
          borderRadius: 8, padding: 16, marginBottom: 24,
        }}>
          <p style={{ color: "#a78bfa", fontWeight: 700, marginBottom: 6, fontSize: "0.85rem" }}>
            ⚡ FINAL VERDICT
          </p>
          <p style={{ color: "#e5e7eb", margin: 0, fontSize: "0.9rem", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
            {report.verdict}
          </p>
        </div>

        {/* Agent reports */}
        <AgentSection title="Security"     emoji="🔐" data={report.security}     />
        <AgentSection title="Performance"  emoji="🐌" data={report.performance}  />
        <AgentSection title="Architecture" emoji="🏗️" data={report.architecture} />
        <AgentSection title="Scalability"  emoji="📈" data={report.scalability}  />
      </div>
    </div>
  );
}

// ─── Main Chat component ────────────────────────────────────────────────────

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages]   = useState([]);
  const [loading, setLoading]     = useState(false);

  // review state
  const [reviewing, setReviewing]   = useState(false);
  const [reviewStage, setReviewStage] = useState(""); // progress label
  const [report, setReport]         = useState(null);

  const location = useLocation();
  const repoId   = location.state?.repoId;

  // ── Chat ──────────────────────────────────────────────────────────────────
  const sendMessage = async () => {
    if (!question || loading) return;
    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);
    try {
      const res = await chat(repoId, question);
      setMessages((prev) => [...prev, { role: "bot", text: res.data.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "Error reaching backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  // ── Review ────────────────────────────────────────────────────────────────
  const STAGES = [
    "🔐 Running Security Agent…",
    "🐌 Running Performance Agent…",
    "🏗️  Running Architecture Agent…",
    "📈 Running Scalability Agent…",
    "💀 Generating brutal verdict…",
  ];

  const startReview = async () => {
    setReviewing(true);
    setReport(null);

    // Cycle through stage labels while waiting
    let stageIdx = 0;
    setReviewStage(STAGES[0]);
    const interval = setInterval(() => {
      stageIdx = (stageIdx + 1) % STAGES.length;
      setReviewStage(STAGES[stageIdx]);
    }, 2500);

    try {
      const res = await reviewRepo(repoId);
      setReport(res.data);
    } catch (e) {
      alert("Review failed: " + (e.response?.data?.detail || e.message));
    } finally {
      clearInterval(interval);
      setReviewing(false);
      setReviewStage("");
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div style={{
      minHeight: "100vh",
      background: "#050510",
      color: "#e5e7eb",
      fontFamily: "'Inter', sans-serif",
      display: "flex",
      flexDirection: "column",
    }}>

      {/* Header */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "14px 24px",
        borderBottom: "1px solid #1f2937",
        background: "#0a0a1a",
      }}>
        <span style={{ fontWeight: 700, color: "#818cf8", fontSize: "1.1rem" }}>🧠 Repo IQ</span>
        <button
          onClick={startReview}
          disabled={reviewing}
          style={{
            background: reviewing ? "#1f2937" : "linear-gradient(135deg, #7c3aed, #ef4444)",
            border: "none",
            color: "#fff",
            borderRadius: 8,
            padding: "8px 18px",
            fontWeight: 700,
            cursor: reviewing ? "not-allowed" : "pointer",
            fontSize: "0.9rem",
            transition: "opacity .2s",
            opacity: reviewing ? 0.7 : 1,
          }}
        >
          {reviewing ? reviewStage : "🔥 Roast this Repo"}
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.length === 0 && (
          <p style={{ color: "#374151", textAlign: "center", marginTop: 60 }}>
            Ask anything about the indexed repository…
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{
            alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
            maxWidth: "75%",
            background: msg.role === "user" ? "#4f46e5" : "#1f2937",
            borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
            padding: "10px 16px",
            fontSize: "0.9rem",
            lineHeight: 1.6,
            whiteSpace: "pre-wrap",
          }}>
            {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: "flex-start", color: "#6b7280", fontSize: "0.85rem" }}>
            thinking…
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{
        padding: "14px 24px",
        borderTop: "1px solid #1f2937",
        background: "#0a0a1a",
        display: "flex",
        gap: 10,
      }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about this repo…"
          style={{
            flex: 1,
            background: "#1f2937",
            border: "1px solid #374151",
            borderRadius: 8,
            padding: "10px 14px",
            color: "#e5e7eb",
            fontSize: "0.9rem",
            outline: "none",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !question}
          style={{
            background: "#4f46e5",
            border: "none",
            color: "#fff",
            borderRadius: 8,
            padding: "10px 20px",
            fontWeight: 600,
            cursor: "pointer",
            opacity: loading || !question ? 0.5 : 1,
          }}
        >
          Send
        </button>
      </div>

      {/* Review Modal */}
      {report && <ReviewPanel report={report} onClose={() => setReport(null)} />}
    </div>
  );
}

export default Chat;