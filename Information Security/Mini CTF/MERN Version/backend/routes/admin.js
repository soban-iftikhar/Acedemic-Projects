const express = require('express');
const router = express.Router();
const {
  checkAdmin,
  getAdminStats,
  getAllUsers,
  getSubmissions,
  getChallengeDetails,
  getAllChallengesAdmin,
  createChallenge,
  updateChallenge,
  deleteChallenge
} = require('../controllers/adminController');
const { requireAdmin } = require('../middleware/auth');

// Admin routes
router.get('/check', checkAdmin);
router.get('/stats', requireAdmin, getAdminStats);
router.get('/users', requireAdmin, getAllUsers);
router.get('/submissions', requireAdmin, getSubmissions);
router.get('/challenge/:challengeId', requireAdmin, getChallengeDetails);
router.get('/challenges', requireAdmin, getAllChallengesAdmin);
router.post('/challenges', requireAdmin, createChallenge);
router.put('/challenges/:challengeId', requireAdmin, updateChallenge);
router.delete('/challenges/:challengeId', requireAdmin, deleteChallenge);

module.exports = router;
