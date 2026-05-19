const User = require('../models/User');
const Challenge = require('../models/Challenge');
const Submission = require('../models/Submission');

const getChallengePointMap = async () => {
  const challenges = await Challenge.find().select('id points');
  return new Map(challenges.map((challenge) => [challenge.id, Number(challenge.points) || 0]));
};

const ensureUserTotalPoints = async (user, challengePointMap) => {
  let updated = false;
  let recalculatedPoints = 0;

  user.solvedChallenges.forEach((solved) => {
    let points = Number(solved?.points);
    if (!Number.isFinite(points)) {
      points = challengePointMap.get(solved.challengeId) || 0;
      solved.points = points;
      updated = true;
    }
    recalculatedPoints += points;
  });

  if (!Number.isFinite(user.totalPoints) || user.totalPoints !== recalculatedPoints) {
    user.totalPoints = recalculatedPoints;
    updated = true;
  }

  if (updated) {
    await user.save();
  }

  return user.totalPoints;
};

// Check if user is admin
const checkAdmin = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    res.json({ isAdmin: true, username: user.username });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get admin statistics
const getAdminStats = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const totalUsers = await User.countDocuments({ isAdmin: false });
    const totalChallenges = await Challenge.countDocuments();
    const totalSubmissions = await Submission.countDocuments();
    const correctSubmissions = await Submission.countDocuments({ isCorrect: true });
    const challengePointMap = await getChallengePointMap();
    
    // Get leaderboard
    const leaderboard = await User.find({ isAdmin: false })
      .select('username totalPoints solvedChallenges')
      .sort({ totalPoints: -1 })
      .limit(10);

    const normalizedLeaderboard = [];
    for (const entry of leaderboard) {
      const points = await ensureUserTotalPoints(entry, challengePointMap);
      normalizedLeaderboard.push({
        username: entry.username,
        points,
        solved: entry.solvedChallenges.length
      });
    }

    normalizedLeaderboard.sort((a, b) => b.points - a.points);

    // Get recent submissions
    const recentSubmissions = await Submission.find()
      .sort({ submittedAt: -1 })
      .limit(20)
      .select('username challengeName flag isCorrect submittedAt');

    res.json({
      totalUsers,
      totalChallenges,
      totalSubmissions,
      correctSubmissions,
      solveRate: totalSubmissions > 0 ? ((correctSubmissions / totalSubmissions) * 100).toFixed(2) : 0,
      leaderboard: normalizedLeaderboard,
      recentSubmissions
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get all users
const getAllUsers = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const users = await User.find({ isAdmin: false })
      .select('username email totalPoints solvedChallenges createdAt')
      .sort({ totalPoints: -1 });

    const challengePointMap = await getChallengePointMap();

    const normalizedUsers = [];
    for (const entry of users) {
      const points = await ensureUserTotalPoints(entry, challengePointMap);
      normalizedUsers.push({
        id: entry._id,
        username: entry.username,
        email: entry.email,
        points,
        solved: entry.solvedChallenges.length,
        joinedAt: entry.createdAt
      });
    }

    normalizedUsers.sort((a, b) => b.points - a.points);

    res.json(normalizedUsers);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const getAllChallengesAdmin = async (req, res) => {
  try {
    const challenges = await Challenge.find().sort({ createdAt: 1 });
    res.json(challenges);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const createChallenge = async (req, res) => {
  try {
    const { id, slug, name, description, category, difficulty, points, flag } = req.body;

    if (!id || !slug || !name || !description || !difficulty || points === undefined || !flag) {
      return res.status(400).json({ error: 'id, slug, name, description, difficulty, points and flag are required' });
    }

    const normalizedId = String(id).trim().toLowerCase();
    const normalizedSlug = String(slug).trim().toLowerCase();

    const existing = await Challenge.findOne({ $or: [{ id: normalizedId }, { slug: normalizedSlug }] });
    if (existing) {
      return res.status(400).json({ error: 'Challenge with this id or slug already exists' });
    }

    const challenge = await Challenge.create({
      id: normalizedId,
      slug: normalizedSlug,
      name: String(name).trim(),
      description: String(description).trim(),
      category: category ? String(category).trim() : 'General',
      difficulty,
      points: Number(points),
      flag: String(flag).trim()
    });

    res.status(201).json(challenge);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const updateChallenge = async (req, res) => {
  try {
    const { challengeId } = req.params;
    const { slug, name, description, category, difficulty, points, flag } = req.body;

    const challenge = await Challenge.findOne({ id: challengeId });
    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    if (slug !== undefined) challenge.slug = String(slug).trim().toLowerCase();
    if (name !== undefined) challenge.name = String(name).trim();
    if (description !== undefined) challenge.description = String(description).trim();
    if (category !== undefined) challenge.category = String(category).trim();
    if (difficulty !== undefined) challenge.difficulty = difficulty;
    if (points !== undefined) challenge.points = Number(points);
    if (flag !== undefined) challenge.flag = String(flag).trim();

    await challenge.save();
    res.json(challenge);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const deleteChallenge = async (req, res) => {
  try {
    const { challengeId } = req.params;
    const challenge = await Challenge.findOne({ id: challengeId });

    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    const removedChallengePoint = Number(challenge.points) || 0;

    const users = await User.find({ 'solvedChallenges.challengeId': challengeId });
    for (const user of users) {
      user.solvedChallenges = user.solvedChallenges.filter((entry) => entry.challengeId !== challengeId);
      user.totalPoints = Number.isFinite(user.totalPoints)
        ? Math.max(0, user.totalPoints - removedChallengePoint)
        : user.solvedChallenges.reduce((total, solved) => total + (Number(solved?.points) || 0), 0);
      await user.save();
    }

    await Submission.deleteMany({ challengeId });
    await challenge.deleteOne();

    res.json({ success: true, message: 'Challenge deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get submissions
const getSubmissions = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const { challengeId, page = 1, limit = 50 } = req.query;
    const skip = (page - 1) * limit;

    let query = {};
    if (challengeId) {
      query.challengeId = challengeId;
    }

    const submissions = await Submission.find(query)
      .sort({ submittedAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Submission.countDocuments(query);

    res.json({
      submissions,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get challenge details with analytics
const getChallengeDetails = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const { challengeId } = req.params;
    const challenge = await Challenge.findOne({ id: challengeId });

    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    const submissions = await Submission.countDocuments({ challengeId });
    const correctSubmissions = await Submission.countDocuments({ challengeId, isCorrect: true });

    res.json({
      ...challenge.toObject(),
      totalSubmissions: submissions,
      correctSubmissions,
      solveRate: submissions > 0 ? ((correctSubmissions / submissions) * 100).toFixed(2) : 0
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = {
  checkAdmin,
  getAdminStats,
  getAllUsers,
  getSubmissions,
  getChallengeDetails,
  getAllChallengesAdmin,
  createChallenge,
  updateChallenge,
  deleteChallenge
};
