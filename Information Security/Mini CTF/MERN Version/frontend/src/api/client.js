import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true
});

export const authAPI = {
  register: (username, email, password, confirmPassword) =>
    api.post('/auth/register', { username, email, password, confirmPassword }),
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  logout: () =>
    api.post('/auth/logout'),
  getCurrentUser: () =>
    api.get('/auth/me')
};

export const challengesAPI = {
  getAllChallenges: () =>
    api.get('/challenges'),
  getChallenge: (id) =>
    api.get(`/challenges/${id}`),
  submitFlag: (challengeId, flag) =>
    api.post('/challenges/submit', { challengeId, flag }),
  getChallengeStats: () =>
    api.get('/challenges/stats'),
  getUserProgress: () =>
    api.get('/challenges/progress'),
  getIdorProfile: (id) =>
    api.get('/challenges/idor/profile', { params: { id } }),
  getBacSecretPanel: () =>
    api.get('/challenges/bac/secret-panel'),
  getLeaderboard: () =>
    api.get('/challenges/leaderboard')
};

export const adminAPI = {
  checkAdmin: () =>
    api.get('/admin/check'),
  getAdminStats: () =>
    api.get('/admin/stats'),
  getChallenges: () =>
    api.get('/admin/challenges'),
  createChallenge: (payload) =>
    api.post('/admin/challenges', payload),
  updateChallenge: (challengeId, payload) =>
    api.put(`/admin/challenges/${challengeId}`, payload),
  deleteChallenge: (challengeId) =>
    api.delete(`/admin/challenges/${challengeId}`),
  getAllUsers: () =>
    api.get('/admin/users'),
  getSubmissions: (challengeId, page, limit) =>
    api.get('/admin/submissions', { params: { challengeId, page, limit } }),
  getChallengeDetails: (challengeId) =>
    api.get(`/admin/challenge/${challengeId}`)
};

export default api;
