const mongoose = require("mongoose");

async function connectDb(mongoUri) {
  await mongoose.connect(mongoUri);
  console.log("[server] MongoDB connected");
}

module.exports = { connectDb };
