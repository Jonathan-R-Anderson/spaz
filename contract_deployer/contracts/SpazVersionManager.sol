// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpazVersionManager {
    address public owner;
    string public versionNumber;
    uint256 public developmentFeeRate; // e.g., 250 = 2.5%

    mapping(string => bytes32) public fileHashes; // filename => sha256 hash
    mapping(string => string) public domainVersions; // domain => version

    event VersionUpdated(string version);
    event FileHashUpdated(string fileName, bytes32 hash);
    event DevFeeUpdated(uint256 newRate);
    event DomainRegistered(string domain, string version);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor(string memory initialVersion, uint256 initialFeeRate) {
        owner = msg.sender;
        versionNumber = initialVersion;
        developmentFeeRate = initialFeeRate;
    }

    // --- Owner Functions ---

    function updateVersion(string memory newVersion) public onlyOwner {
        versionNumber = newVersion;
        emit VersionUpdated(newVersion);
    }

    function updateDevFeeRate(uint256 newRate) public onlyOwner {
        developmentFeeRate = newRate;
        emit DevFeeUpdated(newRate);
    }

    function setFileHash(string memory fileName, bytes32 hash) public onlyOwner {
        fileHashes[fileName] = hash;
        emit FileHashUpdated(fileName, hash);
    }

    function batchSetFileHashes(string[] memory fileNames, bytes32[] memory hashes) public onlyOwner {
        require(fileNames.length == hashes.length, "Array lengths mismatch");
        for (uint256 i = 0; i < fileNames.length; i++) {
            fileHashes[fileNames[i]] = hashes[i];
            emit FileHashUpdated(fileNames[i], hashes[i]);
        }
    }

    // --- Reader Reporting ---

    function registerDomainVersion(string memory domain, string memory version) public {
        domainVersions[domain] = version;
        emit DomainRegistered(domain, version);
    }

    function getDomainVersion(string memory domain) public view returns (string memory) {
        return domainVersions[domain];
    }

    // --- View Functions ---

    function getFileHash(string memory fileName) public view returns (bytes32) {
        return fileHashes[fileName];
    }

    function getDevFeeRate() public view returns (uint256) {
        return developmentFeeRate;
    }

    function getVersion() public view returns (string memory) {
        return versionNumber;
    }
}
