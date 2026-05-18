const mongoose = require("mongoose");

const xssMessageSchema = new mongoose.Schema(
  {
    username: { type: String, required: true },
    message: { type: String, required: true }
  },
  { timestamps: true }
);

xssMessageSchema.index({ createdAt: -1 });

module.exports = mongoose.model("XssMessage", xssMessageSchema);
