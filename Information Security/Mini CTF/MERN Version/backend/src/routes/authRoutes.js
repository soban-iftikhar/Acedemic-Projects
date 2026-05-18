const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const User = require("../models/User");
const { authenticate } = require("../middleware/auth");
const { logActivity } = require("../middleware/logActivity");

const router = express.Router();

function setAuthCookie(res, token) {
  res.cookie("token", token, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    maxAge: 1000 * 60 * 60 * 8
  });
}

router.post("/register", async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const existing = await User.findOne({ $or: [{ username }, { email }] });
    if (existing) {
      return res.status(409).json({ message: "Username or email already exists" });
    }

    const hash = await bcrypt.hash(password, 10);
    const user = await User.create({ username, email, password: hash, role: "player", score: 0 });

    await logActivity({
      userId: user._id,
      action: "REGISTER_SUCCESS",
      payload: `user=${username}`,
      ipAddress: req.ip
    });

    return res.status(201).json({ message: "Registration successful" });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
});

router.post("/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user) {
      await logActivity({ action: "LOGIN_FAIL", payload: `user=${username}`, ipAddress: req.ip });
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const ok = await bcrypt.compare(password, user.password);
    if (!ok) {
      await logActivity({ action: "LOGIN_FAIL", payload: `user=${username}`, ipAddress: req.ip });
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "8h" });
    setAuthCookie(res, token);

    await logActivity({
      userId: user._id,
      action: "LOGIN_SUCCESS",
      payload: `user=${username}`,
      ipAddress: req.ip
    });

    return res.json({
      message: "Login successful",
      user: { id: user._id, username: user.username, role: user.role, score: user.score }
    });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
});

router.post("/logout", (req, res) => {
  res.clearCookie("token");
  return res.json({ message: "Logged out" });
});

router.get("/me", authenticate, (req, res) => {
  return res.json({ user: req.user });
});

module.exports = router;
