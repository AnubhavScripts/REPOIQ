import axios from "axios";

const API = axios.create(
    {
       baseURL:import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
    }
);

export const ingestRepo = async (repoUrl) => {
    return API.post("/api/ingest", { repo_url: repoUrl });
};

export const getRepoStatus = async (repoId) => {
    return API.get(`/api/status/${repoId}`);
};

export const chat = async (repoId, question) => {
    return API.post("/api/chat", {
        repo_id: repoId,
        question: question,
    });
};
