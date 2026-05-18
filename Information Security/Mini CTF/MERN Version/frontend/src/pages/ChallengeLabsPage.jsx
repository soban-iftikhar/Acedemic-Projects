import { useState } from "react";
import api from "../lib/api";

export default function ChallengeLabsPage() {
  const [out, setOut] = useState("");
  const [forms, setForms] = useState({
    sqliUser: "' OR '1'='1",
    sqliPass: "x",
    idorId: "",
    xss: "<script>alert(document.cookie)</script>",
    crypto: "",
    hash: "password",
    rsa: "65",
    brute: "letmein",
    diffie: "2",
    vigenere: "flag{v1g3n3r3_c1ph3r_cr4ck3d}"
  });

  function set(name, value) {
    setForms((f) => ({ ...f, [name]: value }));
  }

  async function run(label, request) {
    try {
      const { data } = await request();
      setOut(`${label}\n${JSON.stringify(data, null, 2)}`);
    } catch (err) {
      setOut(`${label}\n${JSON.stringify(err?.response?.data || { message: err.message }, null, 2)}`);
    }
  }

  return (
    <div className="container">
      <h1>Challenge Labs (Direct Endpoint Testing)</h1>
      <p>Use this page to interact with challenge-specific APIs quickly.</p>

      <div className="grid">
        <article className="card">
          <h3>SQLi</h3>
          <input value={forms.sqliUser} onChange={(e) => set("sqliUser", e.target.value)} />
          <input value={forms.sqliPass} onChange={(e) => set("sqliPass", e.target.value)} />
          <button onClick={() => run("SQLi", () => api.post("/challenges/sqli", { username: forms.sqliUser, password: forms.sqliPass }))}>Run</button>
        </article>

        <article className="card">
          <h3>IDOR</h3>
          <input placeholder="id (optional)" value={forms.idorId} onChange={(e) => set("idorId", e.target.value)} />
          <button onClick={() => run("IDOR", () => api.get(`/challenges/idor/profile${forms.idorId ? `?id=${forms.idorId}` : ""}`))}>Run</button>
        </article>

        <article className="card">
          <h3>XSS</h3>
          <input value={forms.xss} onChange={(e) => set("xss", e.target.value)} />
          <button onClick={() => run("XSS POST", () => api.post("/challenges/xss", { message: forms.xss }))}>Post</button>
          <button onClick={() => run("XSS GET", () => api.get("/challenges/xss"))}>Fetch</button>
        </article>

        <article className="card">
          <h3>BAC</h3>
          <button onClick={() => run("BAC secret", () => api.get("/challenges/bac/secret-panel"))}>Access Secret Panel</button>
        </article>

        <article className="card">
          <h3>Crypto</h3>
          <input placeholder="decoded flag" value={forms.crypto} onChange={(e) => set("crypto", e.target.value)} />
          <button onClick={() => run("Crypto read", () => api.get("/challenges/crypto"))}>Get Encoded</button>
          <button onClick={() => run("Crypto submit", () => api.post("/challenges/crypto", { decoded: forms.crypto }))}>Submit</button>
        </article>

        <article className="card">
          <h3>Hash</h3>
          <input value={forms.hash} onChange={(e) => set("hash", e.target.value)} />
          <button onClick={() => run("Hash", () => api.post("/challenges/hash", { cracked: forms.hash }))}>Submit</button>
        </article>

        <article className="card">
          <h3>RSA</h3>
          <input value={forms.rsa} onChange={(e) => set("rsa", e.target.value)} />
          <button onClick={() => run("RSA", () => api.post("/challenges/rsa", { plaintext: forms.rsa }))}>Submit</button>
        </article>

        <article className="card">
          <h3>Bruteforce</h3>
          <input value={forms.brute} onChange={(e) => set("brute", e.target.value)} />
          <button onClick={() => run("Bruteforce", () => api.post("/challenges/bruteforce", { password: forms.brute }))}>Submit</button>
        </article>

        <article className="card">
          <h3>Diffie</h3>
          <input value={forms.diffie} onChange={(e) => set("diffie", e.target.value)} />
          <button onClick={() => run("Diffie", () => api.post("/challenges/diffie", { sharedSecret: forms.diffie }))}>Submit</button>
        </article>

        <article className="card">
          <h3>Vigenere</h3>
          <input value={forms.vigenere} onChange={(e) => set("vigenere", e.target.value)} />
          <button onClick={() => run("Vigenere", () => api.post("/challenges/vigenere", { decoded: forms.vigenere }))}>Submit</button>
        </article>
      </div>

      <pre className="card output">{out || "No response yet"}</pre>
    </div>
  );
}
