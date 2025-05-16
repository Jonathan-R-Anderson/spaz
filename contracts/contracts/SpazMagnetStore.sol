// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpazMagnetStore {
    address public trustedVerifier;

    // domain => owner
    mapping(string => address) public domainOwners;

    // domain => magnet links
    mapping(string => string[]) private magnetUrls;

    mapping(string => string) public domainToMagnet;


    modifier onlyDomainOwner(string memory domain) {
        require(domainOwners[domain] == msg.sender, "Not domain owner");
        _;
    }

    constructor(address _trustedVerifier) {
        trustedVerifier = _trustedVerifier;
    }

    function claimDomain(
        string memory domain,
        bytes memory signature
    ) public {
        require(domainOwners[domain] == address(0), "Domain already claimed");

        bytes32 message = prefixed(keccak256(abi.encodePacked(msg.sender, domain)));
        require(recoverSigner(message, signature) == trustedVerifier, "Invalid signature");

        domainOwners[domain] = msg.sender;
    }

    function addMagnet(string memory domain, string memory url) public onlyDomainOwner(domain) {
        magnetUrls[domain].push(url);
    }

    function getMagnets(string memory domain) public view returns (string[] memory) {
        return magnetUrls[domain];
    }

    // --- Signature helpers ---

    function recoverSigner(bytes32 message, bytes memory sig) internal pure returns (address) {
        require(sig.length == 65, "invalid signature length");
        bytes32 r;
        bytes32 s;
        uint8 v;

        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }

        return ecrecover(message, v, r, s);
    }

    function prefixed(bytes32 hash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }

    function getMagnetForDomain(string memory domain) public view returns (string memory) {
    return domainToMagnet[domain];
}
}
