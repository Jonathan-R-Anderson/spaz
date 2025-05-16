const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const cors = require('cors');
const ethers = require('ethers');
require("dotenv").config();

// Validate and load private key
let privateKey = process.env.PRIVATE_KEY;
if (!privateKey) throw new Error("Missing PRIVATE_KEY in environment");

if (!privateKey.startsWith("0x")) privateKey = "0x" + privateKey;
if (privateKey.length !== 66) throw new Error("PRIVATE_KEY must be 64 hex chars with optional '0x' prefix");

const wallet = new ethers.Wallet(privateKey);
console.log(`[INFO] Wallet loaded: ${wallet.address}`);

// Express setup
const app = express();
app.use(cors());
app.use(bodyParser.json());

const port = process.env.PORT || 4000;

// In-memory challenge store
const challenges = {}; // domain => { challenge, address, expires }

// Step 1: Issue a challenge
app.post('/request-claim', (req, res) => {
  const { domain, address } = req.body;
  if (!domain || !address) {
    return res.status(400).json({ error: 'Missing domain or address' });
  }

  const challenge = crypto.randomBytes(16).toString('hex');
  challenges[domain] = {
    challenge,
    address,
    expires: Date.now() + 5 * 60 * 1000 // 5 minutes
  };

  return res.json({
    challenge,
    instructions: `Please place this string in https://${domain}/.well-known/spaz-challenge.txt`
  });
});

// Step 2: Verify the file and sign the proof
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));

app.post('/verify-claim', async (req, res) => {
  const { domain } = req.body;
  const record = challenges[domain];

  if (!record || Date.now() > record.expires) {
    return res.status(400).json({ error: 'Challenge expired or not found' });
  }

  try {
    const url = `https://${domain}/.well-known/spaz-challenge.txt`;
    const response = await fetch(url);
    const body = await response.text();

    if (body.trim() !== record.challenge) {
      return res.status(400).json({ error: 'Challenge file mismatch' });
    }

    const messageHash = ethers.utils.solidityKeccak256(
      ['address', 'string'],
      [record.address, domain]
    );

    const signature = await wallet.signMessage(ethers.utils.arrayify(messageHash));
    delete challenges[domain];

    return res.json({ signature });
  } catch (err) {
    console.error('[ERROR] Failed to fetch or sign challenge:', err.message);
    return res.status(500).json({ error: 'Internal error verifying challenge' });
  }
});

app.listen(port, () => {
  console.log(`[INFO] Verifier server running on port ${port}`);
});
