const mongoose = require("mongoose");

const challengeSchema = new mongoose.Schema(
  {
    slug: { type: String, required: true, unique: true, index: true },
    title: { type: String, required: true },
    category: { type: String, required: true },
    difficulty: { type: String, required: true },
    points: { type: Number, required: true },
    description: { type: String, required: true },
    hint: { type: String, default: "" },
    hintCost: { type: Number, default: 30 },
    flag: { type: String, required: true },
    active: { type: Boolean, default: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model("Challenge", challengeSchema);
