const express = require("express");
const Challenge = require("../models/Challenge");
const Submission = require("../models/Submission");
const User = require("../models/User");
const { authenticate } = require("../middleware/auth");
const { logActivity } = require("../middleware/logActivity");

const router = express.Router();

async function getSolvedChallengeIds(userId) {
  const solved = await Submission.find({ userId, correct: true }).select("challengeId").lean();
  return solved.map((row) => String(row.challengeId));
}

router.get("/dashboard", authenticate, async (req, res) => {
  const challenges = await Challenge.find({ active: true }).lean();
  const solvedIds = await getSolvedChallengeIds(req.user._id);
  return res.json({
    user: req.user,
    total: challenges.length,
    solvedIds,
    challenges
  });
});

router.get("/challenges", authenticate, async (req, res) => {
  const challenges = await Challenge.find({ active: true }).lean();
  const solvedIds = await getSolvedChallengeIds(req.user._id);
  return res.json({ user: req.user, solvedIds, challenges });
});

router.get("/challenge/:slug", authenticate, async (req, res) => {
  const challenge = await Challenge.findOne({ slug: req.params.slug, active: true }).lean();
  if (!challenge) {
    return res.status(404).json({ message: "Challenge not found" });
  }

  const solvedIds = await getSolvedChallengeIds(req.user._id);
  const alreadySolved = solvedIds.includes(String(challenge._id));
  return res.json({ user: req.user, challenge, alreadySolved });
});

router.post("/submit/:slug", authenticate, async (req, res) => {
  const challenge = await Challenge.findOne({ slug: req.params.slug, active: true });
  if (!challenge) {
    return res.status(404).json({ message: "Challenge not found" });
  }

  const alreadySolved = await Submission.findOne({
    userId: req.user._id,
    challengeId: challenge._id,
    correct: true
  });

  if (alreadySolved) {
    return res.status(200).json({ message: "Already solved", alreadySolved: true });
  }

  const submittedFlag = (req.body.flag || "").trim();
  const correct = submittedFlag === challenge.flag;

  let firstBlood = false;
  if (correct) {
    const prior = await Submission.findOne({ challengeId: challenge._id, correct: true });
    firstBlood = !prior;
  }

  await Submission.create({
    userId: req.user._id,
    challengeId: challenge._id,
    submittedFlag,
    correct,
    firstBlood
  });

  if (correct) {
    await User.updateOne({ _id: req.user._id }, { $inc: { score: challenge.points } });
  }

  await logActivity({
    userId: req.user._id,
    action: "FLAG_SUBMIT",
    payload: `challenge=${challenge.slug} flag=${submittedFlag} correct=${correct}`,
    ipAddress: req.ip
  });

  return res.json({
    correct,
    firstBlood,
    pointsAwarded: correct ? challenge.points : 0,
    message: correct ? "Correct flag" : "Wrong flag"
  });
});

router.post("/hint/:slug", authenticate, async (req, res) => {
  const challenge = await Challenge.findOne({ slug: req.params.slug, active: true });
  if (!challenge) {
    return res.status(404).json({ message: "Challenge not found" });
  }

  const user = await User.findById(req.user._id);
  if (user.score < challenge.hintCost) {
    return res.status(400).json({ message: "Not enough points", cost: challenge.hintCost });
  }

  user.score -= challenge.hintCost;
  await user.save();

  return res.json({ hint: challenge.hint, remainingScore: user.score, cost: challenge.hintCost });
});

router.get("/scoreboard", authenticate, async (req, res) => {
  const players = await User.find({ role: "player" }).select("username score").sort({ score: -1 }).lean();

  const ids = players.map((p) => p._id);
  const counts = await Submission.aggregate([
    { $match: { userId: { $in: ids }, correct: true } },
    { $group: { _id: "$userId", solved: { $sum: 1 } } }
  ]);

  const solvedMap = Object.fromEntries(counts.map((row) => [String(row._id), row.solved]));
  const enriched = players.map((p) => ({ ...p, solved: solvedMap[String(p._id)] || 0 }));

  return res.json({ players: enriched });
});

module.exports = router;
