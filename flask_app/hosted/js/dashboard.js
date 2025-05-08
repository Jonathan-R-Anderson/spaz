let web3;
let gremlinLeaderboard;

window.onload = async function() {
    document.body.appendChild(profilePopup);
    console.log("Window loaded.");
    console.log("Natural library check:", window.natural); // Debug check for natural library
    if (typeof window.ethereum !== 'undefined') {
        console.log("MetaMask detected.");
        web3 = new Web3(window.ethereum);

        gsap.fromTo('#connectWalletIcon', { scale: 0.8 }, { scale: 1.2, duration: 0.5, yoyo: true, repeat: -1, ease: 'power1.inOut' });

        try {
            console.log("Requesting MetaMask accounts...");
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            const accounts = await web3.eth.getAccounts();
            if (accounts.length === 0) {
                document.getElementById('connectWalletIcon').style.display = 'block';
            } else {
                currentAccount = accounts[0];
                document.getElementById('connectWalletIcon').style.display = 'none';
                document.getElementById("status").innerText = `Connected account: ${currentAccount}`;
                await initializePyodide();
                initializeContracts();
                console.log("Gremlin contracts initialized successfully.");
                await checkIfAdmin(currentAccount); 
                await loadAndDisplayThreads();
            }

        } catch (error) {
            console.error('MetaMask access error:', error);
            document.getElementById("status").innerText = 'Could not access MetaMask. Please ensure you have authorized access.';
        }
    } else {
        console.log("MetaMask is not installed.");
        document.getElementById("status").innerText = 'MetaMask is not installed. Please install MetaMask to use this DApp.';
    }
};

function initializeContracts() {
    gremlinThreadContract = new web3.eth.Contract(_gremlinThreadABI, _gremlinThreadAddress);
    console.log("Contract instances created.");
}



async function getLeaderboard() {
    try {
        if (!contract) await connectWeb3();
        const entries = await contract.methods.getLeaderboard().call();
        console.log("Leaderboard:", entries);
        return entries.map(entry => ({ entity: entry.entity, score: Number(entry.score) }));
    } catch (error) {
        console.error("Error fetching leaderboard:", error);
    }
}

// Run the function on page load
window.onload = loadScore;
