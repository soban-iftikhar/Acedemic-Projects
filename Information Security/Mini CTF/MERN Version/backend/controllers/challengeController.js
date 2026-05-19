const Challenge = require('../models/Challenge');
const User = require('../models/User');
const Submission = require('../models/Submission');

// Flag definitions for all 11 challenges
const CHALLENGE_FLAGS = {
  'sqli': 'flag{sql_1nj3ct10n_byp4ss_m4st3r}',
  'idor': 'flag{1d0r_pr0f1l3_3num3r4t10n}',
  'xss': 'flag{xss_scr1pt_1nj3ct3d_c00k13}',
  'bac': 'flag{br0k3n_4cc3ss_4dm1n_p4n3l}',
  'hash': 'flag{md5_h4sh_cr4ck3d_3z}',
  'rsa': 'flag{rs4_pr1v4t3_k3y_d3crypt3d}',
  'bruteforce': 'flag{br0t3_f0rc3_w34k_p4ssw0rd}',
  'diffie': 'flag{d1ff13_h3llm4n_k3y_3xch4ng3}',
  'vigenere': 'flag{v1g3n3r3_c1ph3r_cr4ck3d}',
  'caesar': 'flag{c4es4r_sh1ft_7_d3crypt3d}',
  'crypto': 'flag{c4es4r_c1ph3r_r0t13_cr4ck3d}'
};

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

const getIdorProfile = async (req, res) => {
  try {
    const requestedId = req.query.id ? Number(req.query.id) : req.session.publicId;
    const profile = await User.findOne({ publicId: requestedId }).select('publicId username email isAdmin secretData totalPoints createdAt');

    if (!profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    res.json({
      profile: {
        id: profile._id,
        publicId: profile.publicId,
        username: profile.username,
        email: profile.email,
        role: profile.isAdmin ? 'admin' : 'player',
        score: profile.totalPoints,
        // Ensure the intended challenge flag is visible on the admin profile.
        secretData: profile.isAdmin ? CHALLENGE_FLAGS.idor : profile.secretData,
        joinedAt: profile.createdAt
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const getBacSecretPanel = async (req, res) => {
  try {
    res.json({
      success: true,
      flag: CHALLENGE_FLAGS.bac,
      message: 'You accessed the admin panel without admin privileges!'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const getLeaderboard = async (req, res) => {
  try {
    const challengePointMap = await getChallengePointMap();
    const users = await User.find({ isAdmin: false })
      .select('username totalPoints solvedChallenges createdAt')
      .sort({ totalPoints: -1, createdAt: 1 });

    const leaderboard = [];
    for (const user of users) {
      const safePoints = await ensureUserTotalPoints(user, challengePointMap);
      leaderboard.push({
        id: user._id,
        username: user.username,
        points: safePoints,
        solved: user.solvedChallenges.length,
        joinedAt: user.createdAt
      });
    }

    leaderboard.sort((a, b) => b.points - a.points || new Date(a.joinedAt) - new Date(b.joinedAt));

    res.json(leaderboard.map((user, index) => ({
      rank: index + 1,
      ...user
    })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get all challenges
const getAllChallenges = async (req, res) => {
  try {
    const challenges = await Challenge.find().select('-flag');
    res.json(challenges);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get single challenge
const getChallenge = async (req, res) => {
  try {
    const { id } = req.params;
    const challenge = await Challenge.findOne({ id }).select('-flag');
    
    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    res.json(challenge);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Submit flag
const submitFlag = async (req, res) => {
  try {
    if (!req.session.userId) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const { challengeId, flag } = req.body;

    if (!challengeId || !flag) {
      return res.status(400).json({ error: 'Challenge ID and flag required' });
    }

    const challenge = await Challenge.findOne({ id: challengeId });
    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    const user = await User.findById(req.session.userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const challengePointMap = await getChallengePointMap();
    await ensureUserTotalPoints(user, challengePointMap);

    // Check if user already solved this challenge
    const alreadySolved = user.solvedChallenges.find(c => c.challengeId === challengeId);
    if (alreadySolved) {
      return res.json({
        success: true,
        alreadySolved: true,
        message: 'Challenge already solved',
        flag: CHALLENGE_FLAGS[challengeId],
        points: 0,
        totalPoints: user.totalPoints
      });
    }

    // Check flag - case insensitive
    const isCorrect = flag.toLowerCase().trim() === CHALLENGE_FLAGS[challengeId].toLowerCase();

    // Create submission record
    const submission = new Submission({
      userId: user._id,
      username: user.username,
      challengeId,
      challengeName: challenge.name,
      flag,
      isCorrect,
      points: isCorrect ? challenge.points : 0
    });

    await submission.save();

    if (isCorrect) {
      const challengePoints = Number(challenge.points) || 0;

      // Update user's solved challenges
      user.solvedChallenges.push({
        challengeId,
        points: challengePoints
      });
      user.totalPoints += challengePoints;
      await user.save();

      // Update challenge stats
      challenge.solveCount += 1;
      challenge.submissions += 1;

      // Award first blood
      if (challenge.solveCount === 1) {
        challenge.firstBlood = {
          userId: user._id,
          username: user.username,
          solvedAt: new Date()
        };
      }

      await challenge.save();

      res.json({
        success: true,
        message: 'Flag is correct!',
        flag: CHALLENGE_FLAGS[challengeId],
        points: challengePoints,
        totalPoints: user.totalPoints,
        firstBlood: challenge.solveCount === 1
      });
    } else {
      challenge.submissions += 1;
      await challenge.save();

      res.json({
        success: false,
        message: 'Flag is incorrect',
        points: 0
      });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get challenge stats for leaderboard
const getChallengeStats = async (req, res) => {
  try {
    const challenges = await Challenge.find().select('id name points solveCount submissions firstBlood');
    res.json(challenges);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Get user's challenge progress
const getUserProgress = async (req, res) => {
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

    const challenges = await Challenge.find().select('id name points difficulty');
    
    const progress = challenges.map(challenge => {
      const solved = user.solvedChallenges.find(c => c.challengeId === challenge.id);
      return {
        id: challenge.id,
        name: challenge.name,
        points: challenge.points,
        difficulty: challenge.difficulty,
        solved: !!solved,
        solvedAt: solved ? solved.solvedAt : null
      };
    });

    res.json({
      totalPoints: safeTotalPoints,
      solvedCount: user.solvedChallenges.length,
      totalChallenges: challenges.length,
      progress
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = {
  getAllChallenges,
  getChallenge,
  submitFlag,
  getChallengeStats,
  getUserProgress,
  getIdorProfile,
  getBacSecretPanel,
  getLeaderboard
};
