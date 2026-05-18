const User = require('../models/User');
const Submission = require('../models/Submission');
const Challenge = require('../models/Challenge');

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

async function getNextPublicId() {
  const lastUser = await User.findOne().sort({ publicId: -1 }).select('publicId');
  return lastUser?.publicId ? lastUser.publicId + 1 : 1;
}

// Register user
const register = async (req, res) => {
  try {
    const { username, email, password, confirmPassword } = req.body;

    if (!username || !email || !password || !confirmPassword) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    if (password !== confirmPassword) {
      return res.status(400).json({ error: 'Passwords do not match' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters' });
    }

    const existingUser = await User.findOne({ $or: [{ username }, { email }] });
    if (existingUser) {
      return res.status(400).json({ error: 'Username or email already exists' });
    }

    const newUser = new User({ username, email, password, publicId: await getNextPublicId() });
    await newUser.save();

    req.session.userId = newUser._id;
    req.session.username = newUser.username;
    req.session.isAdmin = newUser.isAdmin;
    req.session.publicId = newUser.publicId;

    res.json({ 
      success: true, 
      message: 'Registration successful',
      user: {
        id: newUser._id,
        publicId: newUser.publicId,
        username: newUser.username,
        email: newUser.email,
        isAdmin: newUser.isAdmin,
        totalPoints: newUser.totalPoints,
        solvedChallenges: newUser.solvedChallenges.length
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Login user
const login = async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password required' });
    }

    // Check for SQL Injection vulnerability (vulnerable to SQLi for demonstration)
    const user = await User.findOne({ username });

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const challengePointMap = await getChallengePointMap();
    const safeTotalPoints = await ensureUserTotalPoints(user, challengePointMap);

    req.session.userId = user._id;
    req.session.username = user.username;
    req.session.isAdmin = user.isAdmin;
    req.session.publicId = user.publicId;

    res.json({ 
      success: true, 
      message: 'Login successful',
      user: {
        id: user._id,
        publicId: user.publicId,
        username: user.username,
        email: user.email,
        isAdmin: user.isAdmin,
        totalPoints: safeTotalPoints,
        solvedChallenges: user.solvedChallenges.length
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Logout user
const logout = async (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.clearCookie('connect.sid');
    res.json({ success: true, message: 'Logged out successfully' });
  });
};

// Get current user
const getCurrentUser = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = await User.findById(req.session.userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const challengePointMap = await getChallengePointMap();
    const safeTotalPoints = await ensureUserTotalPoints(user, challengePointMap);

    res.json({
      id: user._id,
      publicId: user.publicId,
      username: user.username,
      email: user.email,
      isAdmin: user.isAdmin,
      totalPoints: safeTotalPoints,
      solvedChallenges: user.solvedChallenges.length
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { register, login, logout, getCurrentUser };
