// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ILivestream {
    function getStreamCreator(uint streamId) external view returns (address);
}

contract SpazModeration {
    address public owner;

    mapping(bytes32 => address) public domainAdmins;
    mapping(bytes32 => mapping(address => bool)) public bannedUsers;
    mapping(bytes32 => mapping(uint => bool)) public blacklistedStreams;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAdmin(bytes32 domain) {
        require(msg.sender == domainAdmins[domain], "Not admin for domain");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerDomain(bytes32 domain, address admin) external onlyOwner {
        domainAdmins[domain] = admin;
    }

    function banUser(bytes32 domain, address user) external onlyAdmin(domain) {
        bannedUsers[domain][user] = true;
    }

    function unbanUser(bytes32 domain, address user) external onlyAdmin(domain) {
        bannedUsers[domain][user] = false;
    }

    function blacklistStream(bytes32 domain, uint streamId) external onlyAdmin(domain) {
        blacklistedStreams[domain][streamId] = true;
    }

    function unblacklistStream(bytes32 domain, uint streamId) external onlyAdmin(domain) {
        blacklistedStreams[domain][streamId] = false;
    }

    function isUserBanned(bytes32 domain, address user) external view returns (bool) {
        return bannedUsers[domain][user];
    }

    function isStreamBlacklisted(bytes32 domain, uint streamId) external view returns (bool) {
        return blacklistedStreams[domain][streamId];
    }

    function hashDomain(string memory domain) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(domain));
    }
}
