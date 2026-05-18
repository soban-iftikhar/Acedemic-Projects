import { useEffect, useState } from "react";
import api from "../lib/api";

export default function ScoreboardPage() {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    (async () => {
      const { data } = await api.get("/player/scoreboard");
      setPlayers(data.players || []);
    })();
  }, []);

  return (
    <div className="container">
      <h1>Scoreboard</h1>
      <table className="table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Score</th>
            <th>Solved</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player, idx) => (
            <tr key={player._id}>
              <td>{idx + 1}</td>
              <td>{player.username}</td>
              <td>{player.score}</td>
              <td>{player.solved}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
