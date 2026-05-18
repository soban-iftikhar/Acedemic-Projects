const express = require('express');
const router = express.Router();
const {
  getAllChallenges,
  getChallenge,
  submitFlag,
  getChallengeStats,
  getUserProgress,
  getIdorProfile,
  getBacSecretPanel,
  getLeaderboard
} = require('../controllers/challengeController');
const { requireAuth } = require('../middleware/auth');

// Challenge routes
router.get('/', getAllChallenges);
router.get('/stats', getChallengeStats);
router.get('/leaderboard', requireAuth, getLeaderboard);
router.get('/progress', requireAuth, getUserProgress);
router.get('/idor/profile', requireAuth, getIdorProfile);
router.get('/bac/secret-panel', requireAuth, getBacSecretPanel);
router.get('/:id', getChallenge);
router.post('/submit', requireAuth, submitFlag);

module.exports = router;
