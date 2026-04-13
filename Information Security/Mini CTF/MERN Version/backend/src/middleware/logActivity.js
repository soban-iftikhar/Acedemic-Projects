const ActivityLog = require("../models/ActivityLog");

async function logActivity({ userId = null, action, payload = "", ipAddress = "" }) {
  try {
    await ActivityLog.create({ userId, action, payload, ipAddress });
  } catch (error) {
    console.error("[logActivity] failed:", error.message);
  }
}

module.exports = { logActivity };
