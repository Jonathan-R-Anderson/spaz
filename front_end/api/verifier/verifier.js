// ✅ 1. BACKEND - Node.js Express Server Example (verifier.js)

const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const cors = require('cors');
const ethers = require('ethers');
require("dotenv").config();
const { Wallet } = require("ethers");

const privateKey = process.env.PRIVATE_KEY;
console.log("[DEBUG] PRIVATE_KEY length:", privateKey?.length);
console.log("[DEBUG] PRIVATE_KEY starts with 0x:", privateKey?.startsWith("0x"));

const wallet = new Wallet(privateKey.startsWith("0x") ? privateKey : "0x" + privateKey);


const app = express();
app.use(cors());
app.use(bodyParser.json());

const port = process.env.PORT || 4000;
const verifierPrivateKey = process.env.VERIFIER_PRIVATE_KEY;
const signer = new ethers.Wallet(verifierPrivateKey);

// Memory store for challenge => user mapping
const challenges = {}; // domain => { challenge, address, expires }

// Step 1: Generate challenge
app.post('/request-claim', (req, res) => {
  const { domain, address } = req.body;
  const challenge = crypto.randomBytes(16).toString('hex');
  challenges[domain] = {
    challenge,
    address,
    expires: Date.now() + 5 * 60 * 1000 // 5 minutes
  };
  res.json({
    challenge,
    instructions: `Please place this string in https://${domain}/.well-known/spaz-challenge.txt`
  });
});

// Step 2: Verify and sign
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));

app.post('/verify-claim', async (req, res) => {
  const { domain } = req.body;
  const record = challenges[domain];
  if (!record || Date.now() > record.expires) return res.status(400).send('Challenge expired or not found');

  try {
    const url = `https://${domain}/.well-known/spaz-challenge.txt`;
    const response = await fetch(url);
    const body = await response.text();

    if (body.trim() !== record.challenge) return res.status(400).send('Challenge file mismatch');

    const message = ethers.utils.solidityKeccak256(['address', 'string'], [record.address, domain]);
    const signature = await signer.signMessage(ethers.utils.arrayify(message));
    delete challenges[domain];
    res.json({ signature });
  } catch (e) {
    res.status(500).send('Error verifying challenge file');
  }
});

app.listen(port, () => console.log(`Verifier running on port ${port}`));
