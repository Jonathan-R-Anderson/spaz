// contracts/api/routes.js
const express = require("express");
const { deployContracts } = require("../lib/deploy");
const fs = require("fs");

const router = express.Router();

router.post("/deploy", async (req, res) => {
  try {
    const output = await deployContracts();
    res.json({ success: true, output });
  } catch (err) {
    console.error("[deploy] Error:", err);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
