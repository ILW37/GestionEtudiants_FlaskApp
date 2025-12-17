import hre from "hardhat";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with address:", deployer.address);

  const Diploma = await hre.ethers.getContractFactory("DiplomaNFT");
  const diploma = await Diploma.deploy("DiplomaNFT", "DPL");

  await diploma.waitForDeployment();

  console.log("✅ DiplomaNFT deployed to:", await diploma.getAddress());
}

await main();
