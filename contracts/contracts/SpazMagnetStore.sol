// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpazMagnetStore {
    mapping(address => string[]) public magnetUrls;
    mapping(address => address) public owners;

    modifier onlyOwner() {
        require(owners[msg.sender] == msg.sender, "Not owner");
        _;
    }

    constructor() {
        owners[msg.sender] = msg.sender;
    }

    function registerOwner() public {
        owners[msg.sender] = msg.sender;
    }

    function addMagnet(string memory url) public onlyOwner {
        magnetUrls[msg.sender].push(url);
    }

    function getMagnets(address addr) public view returns (string[] memory) {
        return magnetUrls[addr];
    }
}