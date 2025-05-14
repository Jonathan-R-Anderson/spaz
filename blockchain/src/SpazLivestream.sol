// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpazLivestream {
    struct StreamSegment {
        string magnetURI;
        uint timestamp;
        uint previousSegmentId;
    }

    struct Stream {
        address creator;
        uint[] segmentIds;
        bool isActive;
    }

    uint public nextStreamId = 1;
    uint public nextSegmentId = 1;

    mapping(uint => Stream) public streams;
    mapping(uint => StreamSegment) public segments;

    // Streamer moderation
    mapping(address => mapping(address => bool)) public viewerBans;
    mapping(address => mapping(address => bool)) public chatBans;

    // Streamer theming
    mapping(address => string) public themeMagnets;

    // --- Events ---
    event StreamStarted(uint indexed streamId, address indexed creator, string firstMagnet);
    event SegmentAdded(uint indexed streamId, uint indexed segmentId, string magnetURI);
    event Tipped(address indexed from, address indexed to, uint amount, uint indexed streamId);
    event ViewerBanned(address indexed streamer, address indexed viewer, string mode);
    event ViewerUnbanned(address indexed streamer, address indexed viewer, string mode);
    event ThemeUpdated(address indexed streamer, string magnetURI);

    // --- Livestream Management ---

    function startStream(string calldata firstMagnetURI) external returns (uint streamId) {
        streamId = nextStreamId++;
        uint segmentId = nextSegmentId++;

        segments[segmentId] = StreamSegment({
            magnetURI: firstMagnetURI,
            timestamp: block.timestamp,
            previousSegmentId: 0
        });

        Stream storage s = streams[streamId];
        s.creator = msg.sender;
        s.isActive = true;
        s.segmentIds.push(segmentId);

        emit StreamStarted(streamId, msg.sender, firstMagnetURI);
    }

    function addSegment(uint streamId, string calldata magnetURI) external {
        Stream storage s = streams[streamId];
        require(s.creator == msg.sender, "Not your stream");
        require(s.isActive, "Stream not active");

        uint previousId = s.segmentIds[s.segmentIds.length - 1];
        uint segmentId = nextSegmentId++;

        segments[segmentId] = StreamSegment({
            magnetURI: magnetURI,
            timestamp: block.timestamp,
            previousSegmentId: previousId
        });

        s.segmentIds.push(segmentId);

        emit SegmentAdded(streamId, segmentId, magnetURI);
    }

    function getSegmentChain(uint streamId) external view returns (uint[] memory) {
        return streams[streamId].segmentIds;
    }

    function getSegment(uint segmentId) external view returns (string memory, uint, uint) {
        StreamSegment storage seg = segments[segmentId];
        return (seg.magnetURI, seg.timestamp, seg.previousSegmentId);
    }

    function getStreamCreator(uint streamId) external view returns (address) {
        return streams[streamId].creator;
    }

    // --- Tipping ---

    function tipStreamer(uint streamId) external payable {
        require(msg.value > 0, "No ETH sent");
        address streamer = streams[streamId].creator;
        require(streamer != address(0), "Invalid stream");

        (bool sent, ) = streamer.call{value: msg.value}("");
        require(sent, "Failed to send tip");

        emit Tipped(msg.sender, streamer, msg.value, streamId);
    }

    // --- Streamer Moderation ---

    function banViewer(address viewer, string calldata mode) external {
        bytes32 m = keccak256(bytes(mode));
        if (m == keccak256("chat")) {
            chatBans[msg.sender][viewer] = true;
        } else if (m == keccak256("view")) {
            viewerBans[msg.sender][viewer] = true;
        } else {
            revert("Invalid mode");
        }

        emit ViewerBanned(msg.sender, viewer, mode);
    }

    function unbanViewer(address viewer, string calldata mode) external {
        bytes32 m = keccak256(bytes(mode));
        if (m == keccak256("chat")) {
            chatBans[msg.sender][viewer] = false;
        } else if (m == keccak256("view")) {
            viewerBans[msg.sender][viewer] = false;
        } else {
            revert("Invalid mode");
        }

        emit ViewerUnbanned(msg.sender, viewer, mode);
    }

    function isBannedFromChat(address streamer, address viewer) external view returns (bool) {
        return chatBans[streamer][viewer];
    }

    function isBannedFromView(address streamer, address viewer) external view returns (bool) {
        return viewerBans[streamer][viewer];
    }

    // --- Theming ---

    function updateThemeMagnet(string calldata magnetURI) external {
        themeMagnets[msg.sender] = magnetURI;
        emit ThemeUpdated(msg.sender, magnetURI);
    }

    function getThemeMagnet(address streamer) external view returns (string memory) {
        return themeMagnets[streamer];
    }
}
