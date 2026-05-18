const dotenv = require("dotenv");
const bcrypt = require("bcryptjs");
const { connectDb } = require("../config/db");
const User = require("../models/User");
const Challenge = require("../models/Challenge");
const { CHALLENGE_SEED, FLAGS } = require("../config/constants");

dotenv.config();

async function seed() {
  await connectDb(process.env.MONGO_URI);

  const admin = await User.findOne({ username: "admin" });
  if (!admin) {
    await User.create({
      username: "admin",
      email: "admin@ctf.local",
      password: await bcrypt.hash("Admin@1337", 10),
      role: "admin",
      score: 0,
      secretData: `flag_holder: ${FLAGS.idor}`
    });
  }

  const player = await User.findOne({ username: "player1" });
  if (!player) {
    await User.create({
      username: "player1",
      email: "player1@ctf.local",
      password: await bcrypt.hash("player123", 10),
      role: "player",
      score: 0,
      secretData: "Nothing interesting here."
    });
  }

  for (const challenge of CHALLENGE_SEED) {
    const exists = await Challenge.findOne({ slug: challenge.slug });
    if (!exists) {
      await Challenge.create(challenge);
    }
  }

  console.log("[seed] completed");
  process.exit(0);
}

seed().catch((error) => {
  console.error("[seed] failed", error);
  process.exit(1);
});
