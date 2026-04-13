const mongoose = require("mongoose");

const userSchema = new mongoose.Schema(
  {
    username: { type: String, required: true, unique: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    password: { type: String, required: true },
    role: { type: String, enum: ["admin", "player"], default: "player" },
    score: { type: Number, default: 0 },
    secretData: { type: String, default: "Nothing here." }
  },
  { timestamps: true }
);

module.exports = mongoose.model("User", userSchema);
