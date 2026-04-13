const mongoose = require("mongoose");

const submissionSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true, index: true },
    challengeId: { type: mongoose.Schema.Types.ObjectId, ref: "Challenge", required: true, index: true },
    submittedFlag: { type: String, required: true },
    correct: { type: Boolean, default: false },
    firstBlood: { type: Boolean, default: false }
  },
  { timestamps: true }
);

submissionSchema.index({ userId: 1, challengeId: 1, correct: 1 });

module.exports = mongoose.model("Submission", submissionSchema);
