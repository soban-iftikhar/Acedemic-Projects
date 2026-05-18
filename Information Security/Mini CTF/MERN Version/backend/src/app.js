const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const dotenv = require("dotenv");
const { connectDb } = require("./config/db");

dotenv.config();

const authRoutes = require("./routes/authRoutes");
const playerRoutes = require("./routes/playerRoutes");
const adminRoutes = require("./routes/adminRoutes");
const challengeRoutes = require("./routes/challengeRoutes");

const app = express();

app.use(
  cors({
    origin: process.env.CLIENT_URL || "http://localhost:5173",
    credentials: true
  })
);
app.use(express.json());
app.use(cookieParser());

app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

app.use("/api/auth", authRoutes);
app.use("/api/player", playerRoutes);
app.use("/api/admin", adminRoutes);
app.use("/api/challenges", challengeRoutes);

app.use((error, req, res, next) => {
  console.error(error);
  return res.status(500).json({ message: "Internal server error" });
});

const port = process.env.PORT || 5000;

async function start() {
  await connectDb(process.env.MONGO_URI);
  app.listen(port, () => {
    console.log(`[server] listening on http://localhost:${port}`);
  });
}

start().catch((error) => {
  console.error("[server] failed to start:", error);
  process.exit(1);
});
