const express = require("express");
const { authenticate } = require("../middleware/auth");
const { logActivity } = require("../middleware/logActivity");
const User = require("../models/User");
const Challenge = require("../models/Challenge");
const XssMessage = require("../models/XssMessage");
const { FLAGS, CRYPTO_ENCODED } = require("../config/constants");

const router = express.Router();
router.use(authenticate);

function rot13(text) {
  return text.replace(/[a-zA-Z]/g, (char) => {
    const base = char <= "Z" ? 65 : 97;
    return String.fromCharCode(((char.charCodeAt(0) - base + 13) % 26) + base);
  });
}

router.post("/sqli", async (req, res) => {
  const { username = "", password = "" } = req.body;
  const queryShown = `SELECT * FROM vuln_users WHERE username='${username}' AND password='${password}'`;

  await logActivity({
    userId: req.user._id,
    action: "SQLI_ATTEMPT",
    payload: `user=${username} pass=${password}`,
    ipAddress: req.ip
  });

  const bypassed = username.includes("' OR '1'='1") || username.includes("' OR 1=1 --");
  const validPair = username === "admin" && password === "S3cr3tP4ss!";

  return res.json({
    queryShown,
    success: bypassed || validPair,
    flag: bypassed || validPair ? FLAGS.sqli : null,
    error: bypassed || validPair ? null : "Invalid credentials"
  });
});

router.get("/idor/profile", async (req, res) => {
  const requested = req.query.id || req.user._id;
  const profile = await User.findById(requested).select("username email role score secretData createdAt").lean();

  await logActivity({
    userId: req.user._id,
    action: "IDOR_ACCESS",
    payload: `requested_id=${requested}`,
    ipAddress: req.ip
  });

  return res.json({ profile, flag: profile && profile.role === "admin" ? FLAGS.idor : null });
});

router.get("/xss", async (req, res) => {
  const messages = await XssMessage.find().sort({ createdAt: -1 }).limit(20).lean();
  res.cookie("ctf_flag", FLAGS.xss, { httpOnly: false, sameSite: "lax" });
  return res.json({ messages });
});

router.post("/xss", async (req, res) => {
  const message = req.body.message || "";
  await XssMessage.create({ username: req.user.username, message });
  await logActivity({ userId: req.user._id, action: "XSS_POST", payload: message.slice(0, 200), ipAddress: req.ip });
  return res.status(201).json({ message: "Posted" });
});

router.get("/bac", async (req, res) => {
  return res.json({
    info: "UI hides admin link, but backend role check on secret endpoint is intentionally missing."
  });
});

router.get("/bac/secret-panel", async (req, res) => {
  await logActivity({ userId: req.user._id, action: "BAC_ACCESS", payload: "secret-panel", ipAddress: req.ip });
  return res.json({ flag: FLAGS.bac });
});

router.get("/crypto", async (req, res) => {
  return res.json({ encoded: CRYPTO_ENCODED, type: "rot13" });
});

router.post("/crypto", async (req, res) => {
  const decoded = (req.body.decoded || "").trim();
  await logActivity({ userId: req.user._id, action: "CRYPTO_ATTEMPT", payload: decoded, ipAddress: req.ip });

  return res.json({
    correct: decoded === FLAGS.crypto,
    expected: rot13(CRYPTO_ENCODED),
    flag: decoded === FLAGS.crypto ? FLAGS.crypto : null
  });
});

router.post("/hash", async (req, res) => {
  const cracked = (req.body.cracked || "").trim().toLowerCase();
  await logActivity({ userId: req.user._id, action: "HASH_ATTEMPT", payload: cracked, ipAddress: req.ip });
  const correct = cracked === "password";
  return res.json({ correct, flag: correct ? FLAGS.hash : null });
});

router.post("/rsa", async (req, res) => {
  const answer = String(req.body.plaintext || "").trim();
  await logActivity({ userId: req.user._id, action: "RSA_ATTEMPT", payload: answer, ipAddress: req.ip });
  const correct = ["65", "A", "a"].includes(answer);
  return res.json({ correct, flag: correct ? FLAGS.rsa : null });
});

router.post("/bruteforce", async (req, res) => {
  const password = (req.body.password || "").trim();
  await logActivity({ userId: req.user._id, action: "BRUTEFORCE_ATTEMPT", payload: password, ipAddress: req.ip });
  const correct = password === "letmein";
  return res.json({ correct, flag: correct ? FLAGS.bruteforce : null });
});

router.post("/diffie", async (req, res) => {
  const sharedSecret = String(req.body.sharedSecret || "").trim();
  await logActivity({ userId: req.user._id, action: "DH_ATTEMPT", payload: sharedSecret, ipAddress: req.ip });
  const correct = sharedSecret === "2";
  return res.json({ correct, flag: correct ? FLAGS.diffie : null });
});

router.post("/vigenere", async (req, res) => {
  const decoded = String(req.body.decoded || "").trim().toLowerCase();
  await logActivity({ userId: req.user._id, action: "VIGENERE_ATTEMPT", payload: decoded, ipAddress: req.ip });
  const correct = decoded === FLAGS.vigenere.toLowerCase();
  return res.json({ correct, flag: correct ? FLAGS.vigenere : null });
});

module.exports = router;
