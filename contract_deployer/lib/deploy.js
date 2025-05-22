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

  let outputLog = [];

  for (const name of CONTRACTS) {
    const artifact = await deployer.loadArtifact(name);
    const contract = await deployer.deploy(artifact, []);
    const abiPath = `${ABI_DIR}/${name}.json`;
    const addressPath = `${ADDRESS_DIR}/${name}.txt`;

    fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
    fs.writeFileSync(addressPath, contract.address);

    const log = `✅ ${name} deployed at ${contract.address}`;
    console.log(log);
    outputLog.push(log);
  }

  return outputLog;
}

module.exports = { deployContracts };
