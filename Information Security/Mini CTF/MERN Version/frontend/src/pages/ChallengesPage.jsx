import { useEffect, useState } from "react";
import api from "../lib/api";

export default function ChallengesPage() {
  const [payload, setPayload] = useState({ challenges: [], solvedIds: [] });
  const [flags, setFlags] = useState({});
  const [status, setStatus] = useState("");

  useEffect(() => {
    (async () => {
      const { data } = await api.get("/player/challenges");
      setPayload(data);
    })();
  }, []);

  async function submit(slug) {
    const flag = flags[slug] || "";
    const { data } = await api.post(`/player/submit/${slug}`, { flag });
    setStatus(`${slug}: ${data.message}`);
  }

  async function hint(slug) {
    try {
      const { data } = await api.post(`/player/hint/${slug}`);
      setStatus(`${slug} hint: ${data.hint}`);
    } catch (err) {
      setStatus(err?.response?.data?.message || "Hint failed");
    }
  }

  return (
    <div className="container">
      <h1>Challenges</h1>
      {status && <p className="success">{status}</p>}
      <div className="grid">
        {payload.challenges.map((c) => (
          <article className="card" key={c._id}>
            <h3>{c.slug.toUpperCase()} - {c.title}</h3>
            <p>{c.description}</p>
            <p>{c.points} pts</p>
            <input
              placeholder="Enter flag"
              value={flags[c.slug] || ""}
              onChange={(e) => setFlags((f) => ({ ...f, [c.slug]: e.target.value }))}
            />
            <div className="inline-actions">
              <button onClick={() => submit(c.slug)}>Submit</button>
              <button onClick={() => hint(c.slug)} className="ghost">Hint</button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
