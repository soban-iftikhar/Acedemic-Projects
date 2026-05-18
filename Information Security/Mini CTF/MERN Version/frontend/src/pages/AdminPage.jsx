import { useEffect, useState } from "react";
import api from "../lib/api";

export default function AdminPage() {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    (async () => {
      const { data } = await api.get("/admin/dashboard");
      setDashboard(data);
    })();
  }, []);

  if (!dashboard) return <div className="container">Loading admin dashboard...</div>;

  return (
    <div className="container">
      <h1>Admin Dashboard</h1>
      <div className="grid">
        <article className="card"><h3>Players</h3><p>{dashboard.totalUsers}</p></article>
        <article className="card"><h3>Challenges</h3><p>{dashboard.totalChallenges}</p></article>
        <article className="card"><h3>Submissions</h3><p>{dashboard.totalSubmissions}</p></article>
        <article className="card"><h3>Correct</h3><p>{dashboard.correctSubmissions}</p></article>
      </div>
      <h2>Recent Logs</h2>
      <div className="card">
        {dashboard.recentLogs.map((log) => (
          <p key={log._id}>
            [{new Date(log.createdAt).toLocaleString()}] {log.action} - {log.payload}
          </p>
        ))}
      </div>
    </div>
  );
}
