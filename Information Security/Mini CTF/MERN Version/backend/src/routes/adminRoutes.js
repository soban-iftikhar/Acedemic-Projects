const express = require("express");
const { authenticate, requireAdmin } = require("../middleware/auth");
const User = require("../models/User");
const Challenge = require("../models/Challenge");
const Submission = require("../models/Submission");
const ActivityLog = require("../models/ActivityLog");

const router = express.Router();
router.use(authenticate, requireAdmin);

router.get("/dashboard", async (req, res) => {
  const [totalUsers, totalChallenges, totalSubmissions, correctSubmissions, recentLogs] = await Promise.all([
    User.countDocuments({ role: "player" }),
    Challenge.countDocuments(),
    Submission.countDocuments(),
    Submission.countDocuments({ correct: true }),
    ActivityLog.find().sort({ createdAt: -1 }).limit(20).lean()
  ]);

  return res.json({
    totalUsers,
    totalChallenges,
    totalSubmissions,
    correctSubmissions,
    recentLogs
  });
});

router.get("/users", async (req, res) => {
  const players = await User.find({ role: "player" }).sort({ score: -1 }).lean();
  const ids = players.map((p) => p._id);
  const solved = await Submission.aggregate([
    { $match: { userId: { $in: ids }, correct: true } },
    { $group: { _id: "$userId", solved: { $sum: 1 } } }
  ]);
  const map = Object.fromEntries(solved.map((row) => [String(row._id), row.solved]));
  return res.json({ players: players.map((p) => ({ ...p, solved: map[String(p._id)] || 0 })) });
});

router.get("/challenges", async (req, res) => {
  const challenges = await Challenge.find().sort({ createdAt: -1 }).lean();
  return res.json({ challenges });
});

router.post("/challenges", async (req, res) => {
  const challenge = await Challenge.create(req.body);
  return res.status(201).json({ challenge });
});

router.put("/challenges/:id", async (req, res) => {
  const challenge = await Challenge.findByIdAndUpdate(req.params.id, req.body, { new: true });
  if (!challenge) {
    return res.status(404).json({ message: "Challenge not found" });
  }
  return res.json({ challenge });
});

router.delete("/challenges/:id", async (req, res) => {
  await Challenge.findByIdAndDelete(req.params.id);
  return res.json({ message: "Challenge deleted" });
});

router.get("/submissions", async (req, res) => {
  const submissions = await Submission.find()
    .populate("userId", "username")
    .populate("challengeId", "title slug")
    .sort({ createdAt: -1 })
    .lean();
  return res.json({ submissions });
});

router.get("/logs", async (req, res) => {
  const logs = await ActivityLog.find().sort({ createdAt: -1 }).limit(300).lean();
  return res.json({ logs });
});

module.exports = router;
