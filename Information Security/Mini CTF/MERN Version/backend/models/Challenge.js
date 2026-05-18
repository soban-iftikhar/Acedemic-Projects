const mongoose = require('mongoose');

const challengeSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  slug: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  category: String,
  difficulty: {
    type: String,
    enum: ['Easy', 'Medium', 'Hard'],
    default: 'Medium'
  },
  points: {
    type: Number,
    required: true,
    default: 100
  },
  flag: {
    type: String,
    required: true
  },
  hints: [String],
  firstBlood: {
    userId: String,
    username: String,
    solvedAt: Date
  },
  submissions: {
    type: Number,
    default: 0
  },
  solveCount: {
    type: Number,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Challenge', challengeSchema);
