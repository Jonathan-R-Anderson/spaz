const { deployContracts } = require("../lib/deploy");
const fs = require("fs");

jest.mock("fs", () => ({
  writeFileSync: jest.fn(),
}));

describe("deployContracts", () => {
  it("should deploy all contracts and write ABI and address", async () => {
    process.env.PRIVATE_KEY = "0x".padEnd(66, "1");
    const logs = await deployContracts();
    expect(logs.length).toBe(3);
    expect(fs.writeFileSync).toHaveBeenCalled();
  });
});
