require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const RPC_URL = process.env.RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;

module.exports = {
  solidity: "0.8.17",
  networks: {
    amoy: {
      url: RPC_URL,           // RPC Polygon Amoy
      accounts: [PRIVATE_KEY]
    }
  }
};
