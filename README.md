<h1 align="center">
  <img src="https://user-images.githubusercontent.com/your-logo.png" width="80" alt="spaz logo"><br>
  <strong>spaz</strong>
  <br><br>
</h1>

<h4 align="center">A decentralized, peer-to-peer content platform built for speed, freedom, and Web3-native interaction.</h4>

<p align="center">
  <em>Forum + Video Streaming — federated, uncensorable, insanely fast.</em>
</p>

---

## 🚀 What is spaz?

**spaz** is a decentralized video streaming and discussion platform built entirely for the modern web. It runs inside your browser, powered by Web3, and orchestrates content through a **federated peer-to-peer network** — no central servers required.

Websites that host `spaz` instances act as **nodes in a swarm**, allowing them to:

- **Orchestrate and mirror each other’s content**
- **Participate in collaborative publishing**
- **Federate user identity, discussion threads, and data streams**
- Seamlessly **distribute video, images, and metadata via BitTorrent**

> Think of it as **Reddit meets Twitch** — but unstoppable, scalable, and composable across the decentralized web.

---

## ✨ Features

- ✅ **Federated P2P architecture** — each node operates independently or in sync
- 🧠 **Web3-native** identity and session management (via Metamask)
- 🌐 **ZKsync Era Mainnet** support for scaling and transaction finality
- 🔥 **Bittorrent-based static file seeding** for resilient, cheap delivery
- 🧵 **Decentralized forum threads** stored on-chain and mirrored
- 🎞️ **Live RTMP + magnet-based archives** — videos are streamable and seeding
- ⚡️ Download **multiple torrents simultaneously**
- 🛡️ Privacy-aware — no trackers, no cookies, no ads

---

## 🧰 Requirements

- 🦊 Metamask
- 🌉 ZKsync Era Mainnet wallet configured
- 🐳 Docker & Docker Compose

---

## 🛠️ Running It

```bash
DOCKER_BUILDKIT=0 sudo docker compose build --progress=plain > build.log
sudo docker compose up
