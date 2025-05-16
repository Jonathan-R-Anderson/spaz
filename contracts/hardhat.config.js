require("@matterlabs/hardhat-zksync-deploy");
require("@nomiclabs/hardhat-ethers");

module.exports = {
  zksolc: {
    version: "1.3.5",
    compilerSource: "binary",
    settings: {
      optimizer: { enabled: true, runs: 200 }
    },
  },
  defaultNetwork: "zksyncMainnet",
  networks: {
    zksyncMainnet: {
      url: "https://mainnet.era.zksync.io",
      ethNetwork: "mainnet",
      zksync: true,
      accounts: [process.env.PRIVATE_KEY]
    }
  },
  solidity: {
    version: "0.8.20"
  }
};
