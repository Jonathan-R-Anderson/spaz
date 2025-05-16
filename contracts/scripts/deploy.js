// contracts/scripts/deploy.js

const { Wallet } = require("zksync-ethers");
const { Deployer } = require("@matterlabs/hardhat-zksync-deploy");
const fs = require("fs");
const hre = require("hardhat");

const CONTRACTS = ["SpazMagnetStore", "SpazLivestream", "SpazModeration"];
const ABI_DIR = "/app/abi";
const ADDRESS_DIR = "/app/address";

async function deployContracts() {
  const wallet = new Wallet(process.env.PRIVATE_KEY);
  const deployer = new Deployer(hre, wallet);

  for (const name of CONTRACTS) {
    const artifact = await deployer.loadArtifact(name);
    const contract = await deployer.deploy(artifact, []);

    const abiPath = `${ABI_DIR}/${name}.json`;
    const addressPath = `${ADDRESS_DIR}/${name}.txt`;

    fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
    fs.writeFileSync(addressPath, contract.address);

    console.log(`✅ ${name} deployed to: ${contract.address}`);
  }
}

deployContracts().catch((err) => {
  console.error("❌ Deployment failed:", err);
  process.exit(1);
});
