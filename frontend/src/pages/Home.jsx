import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { ingestRepo, getRepoStatus } from "../services/api";

const POLL_INTERVAL_MS = 3000; // poll every 3 seconds

function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [phase, setPhase] = useState("idle"); // idle | indexing | done | error
  const [statusMsg, setStatusMsg] = useState("");
  const navigate = useNavigate();
  const pollRef = useRef(null);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const startPolling = (repoId) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await getRepoStatus(repoId);
        const { status, error_message } = res.data;

        if (status === "COMPLETED") {
          stopPolling();
          setPhase("done");
          navigate("/chat", { state: { repoId } });
        } else if (status === "FAILED") {
          stopPolling();
          setPhase("error");
          setStatusMsg(error_message || "Indexing failed. Please try again.");
        } else {
          // PENDING or PROCESSING
          setStatusMsg(
            status === "PROCESSING"
              ? "Cloning & indexing repository…"
              : "Queued for indexing…"
          );
        }
      } catch (err) {
        console.error("Status poll error:", err);
        // keep polling — transient network error
      }
    }, POLL_INTERVAL_MS);
  };

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;
    try {
      setPhase("indexing");
      setStatusMsg("Submitting repository…");
      const response = await ingestRepo(repoUrl);
      const repoId = response.data.repo_id;
      setStatusMsg("Queued for indexing…");
      startPolling(repoId);
    } catch (error) {
      console.error(error);
      setPhase("error");
      setStatusMsg("Could not reach backend. Is the server running?");
    }
  };

  const handleReset = () => {
    stopPolling();
    setPhase("idle");
    setStatusMsg("");
    setRepoUrl("");
  };

  return (
    <div className="h-screen flex flex-col justify-center items-center gap-2">
      <h1 className="text-5xl font-bold">REPOIQ</h1>
      <p className="mt-2 text-slate-400">Analyze any GitHub Repository</p>

      <input
        className="mt-6 p-3 w-[500px] bg-slate-900/50 text-white placeholder-slate-400 border border-slate-700 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-inner disabled:opacity-50"
        placeholder="Paste GitHub repo URL"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        disabled={phase === "indexing"}
      />

      {phase === "idle" || phase === "error" ? (
        <button
          onClick={handleAnalyze}
          className="mt-5 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-medium px-8 py-2.5 rounded-lg shadow-lg hover:shadow-blue-500/20 transition-all duration-200"
        >
          Analyze
        </button>
      ) : null}

      {phase === "indexing" && (
        <div className="mt-5 flex flex-col items-center gap-3">
          {/* Spinner */}
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-300 text-sm">{statusMsg}</p>
          <p className="text-slate-500 text-xs">This may take 30–60 seconds for large repos</p>
        </div>
      )}

      {phase === "error" && (
        <div className="mt-4 flex flex-col items-center gap-2">
          <p className="text-red-400 text-sm text-center max-w-md">{statusMsg}</p>
          <button
            onClick={handleReset}
            className="text-slate-400 underline text-xs hover:text-white transition-colors"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}

export default Home;