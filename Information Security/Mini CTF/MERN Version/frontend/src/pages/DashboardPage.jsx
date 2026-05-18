import { useEffect, useState } from "react";
import api from "../lib/api";

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    (async () => {
      const res = await api.get("/player/dashboard");
      setData(res.data);
    })();
  }, []);

  if (!data) return <div className="container">Loading dashboard...</div>;

  return (
    <div className="container">
      <h1>Player Dashboard</h1>
      <p>
        Total challenges: <b>{data.total}</b> | Solved: <b>{data.solvedIds.length}</b>
      </p>
      <div className="grid">
        {data.challenges.map((c) => (
          <article className="card" key={c._id}>
            <h3>{c.title}</h3>
            <p>{c.category} - {c.difficulty}</p>
            <p>{c.points} pts</p>
          </article>
        ))}
      </div>
    </div>
  );
}
