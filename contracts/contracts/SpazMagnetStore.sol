// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpazMagnetStore {
    address public trustedVerifier;

    // domain => owner
    mapping(string => address) public domainOwners;

    // domain => path => magnet links
    mapping(string => mapping(string => string[])) private domainToPathMagnetUrls;

    // domain => single magnet link (for default path)
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

    // Add magnet link to a specific path on the domain (only domain owner)
    function addMagnetToPath(string memory domain, string memory path, string memory url) public onlyDomainOwner(domain) {
        domainToPathMagnetUrls[domain][path].push(url);
    }

    // Retrieve all magnet links for a given path on a domain
    function getMagnetsForPath(string memory domain, string memory path) public view returns (string[] memory) {
        return domainToPathMagnetUrls[domain][path];
    }

    // Set a single magnet link for the default path of the domain (only domain owner)
    function setMagnetForDomain(string memory domain, string memory url) public onlyDomainOwner(domain) {
        domainToMagnet[domain] = url;
    }

    // Retrieve the single magnet link for the default path on the domain
    function getMagnetForDomain(string memory domain) public view returns (string memory) {
        return bytes(domainToMagnet[domain]).length > 0 ? domainToMagnet[domain] : "No magnet link found";
    }

    // Retrieve the single magnet link for a specific path on the domain
    function getMagnetForDomainAndPath(string memory domain, string memory path) public view returns (string memory) {
        // Return the first magnet link for the specified path on the domain
        string[] memory magnets = domainToPathMagnetUrls[domain][path];
        if (magnets.length > 0) {
            return magnets[0];
        }
        return "No magnet link found for path";
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
}
