import React, { useState, useEffect, useCallback } from 'react';
import { initScrollJack } from '../utils/scrollJack';
import Logo from './Logo';
import ParticleNetwork from './ParticleNetwork';
import { Progress } from "@/components/ui/progress";

// Include Web3.js and WebTorrent.js via CDN
const web3jsScript = document.createElement('script');
web3jsScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/web3/1.6.1/web3.min.js';
document.body.appendChild(web3jsScript);

const webtorrentScript = document.createElement('script');
webtorrentScript.src = 'https://cdn.jsdelivr.net/npm/webtorrent/webtorrent.min.js';
document.body.appendChild(webtorrentScript);

interface LoadingPageProps {
  onComplete: () => void;
  duration?: number;
}

interface MagnetProgress {
  magnetLink: string;
  progress: number;
  downloadRate: number;
  numPeers: number;
}

const LoadingPage: React.FC<LoadingPageProps> = ({ 
  onComplete, 
  duration = 6000 
}) => {
  const [progress, setProgress] = useState(0);
  const [loadingText, setLoadingText] = useState('Initializing blockchain connection...');
  const [web3, setWeb3] = useState<Web3 | null>(null);
  const [torrentClient, setTorrentClient] = useState<WebTorrent | null>(null);
  const [magnetLinks, setMagnetLinks] = useState<string[]>([]); // Store magnet links
  const [contractAddress, setContractAddress] = useState<string | null>(null);
  const [contractABI, setContractABI] = useState<any | null>(null);

  // Track progress of each magnet URL
  const [magnetProgress, setMagnetProgress] = useState<MagnetProgress[]>([]);

  const updateLoadingText = useCallback((prog: number) => {
    if (prog < 0.2) {
      setLoadingText('Initializing blockchain connection...');
    } else if (prog < 0.4) {
      setLoadingText('Establishing peer connection...');
    } else if (prog < 0.6) {
      setLoadingText('Fetching block headers...');
    } else if (prog < 0.8) {
      setLoadingText('Retrieving magnet URLs...');
    } else if (prog < 0.95) {
      setLoadingText('Downloading magnets...');
    } else {
      setLoadingText('Connection established');
    }
  }, []);

  // Initialize Web3 and WebTorrent clients
  useEffect(() => {
    if (typeof window !== "undefined" && window.ethereum) {
      const web3Instance = new Web3(window.ethereum);
      setWeb3(web3Instance);

      // Request account access
      window.ethereum.request({ method: 'eth_requestAccounts' }).then(() => {
        console.log('Web3 initialized');
      }).catch((err: any) => {
        console.error('Web3 error: ', err);
        setLoadingText('Web3 initialization failed.');
      });
    } else {
      console.error('Web3 not available');
    }

    // Initialize WebTorrent.js
    const client = new WebTorrent();
    setTorrentClient(client);
    
    // Cleanup WebTorrent on component unmount
    return () => {
      if (client) {
        client.destroy();
      }
    };
  }, []);

  useEffect(() => {
    updateLoadingText(progress);

    if (progress >= 1) {
      const timer = setTimeout(() => {
        onComplete();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [progress, onComplete, updateLoadingText]);

  useEffect(() => {
    const cleanup = initScrollJack({
      onProgress: (prog) => {
        setProgress(prog);
        updateLoadingText(prog);
      },
      duration,
      onComplete,
    });

    return cleanup;
  }, [duration, onComplete, updateLoadingText]);

  // Fetch Contract Address and ABI from Flask Service
  const fetchContractDetails = async () => {
    try {
      const response = await fetch('http://psichos.is:5005/spaz_magnet_store');
      if (!response.ok) {
        throw new Error('Failed to fetch contract details');
      }
      const data = await response.json();
      setContractAddress(data.address);
      setContractABI(data.abi);
    } catch (error) {
      console.error('Error fetching contract details: ', error);
      setLoadingText('Failed to fetch contract details.');
    }
  };

  // Fetch Magnet URLs from the contract
  const fetchMagnetLinks = async (domain: string, path: string) => {
    if (web3 && contractABI && contractAddress) {
      const contract = new web3.eth.Contract(contractABI, contractAddress);
      try {
        const magnets = await contract.methods.getMagnetsForPath(domain, path).call();
        setMagnetLinks(magnets); // Set the magnet links in state
      } catch (err) {
        console.error('Error fetching magnet links: ', err);
        setLoadingText('Failed to load magnets.');
      }
    }
  };

  // Update the magnet progress
  const updateMagnetProgress = (magnetLink: string, progress: number, downloadRate: number, numPeers: number) => {
    setMagnetProgress((prevState) => {
      const newState = prevState.filter((m) => m.magnetLink !== magnetLink);
      newState.push({ magnetLink, progress, downloadRate, numPeers });
      return newState;
    });
  };

  // Example to load content via WebTorrent (using a magnet link)
  const loadTorrentContent = async (magnetURI: string) => {
    if (torrentClient) {
      torrentClient.add(magnetURI, (torrent) => {
        console.log('Torrent info: ', torrent);

        torrent.on('download', (bytes) => {
          const progress = (torrent.downloaded / torrent.length) * 100;
          const downloadRate = torrent.downloadSpeed / (1024 * 1024); // MB/s
          const numPeers = torrent.numPeers;
          
          updateMagnetProgress(magnetURI, progress, downloadRate, numPeers);

          setProgress(progress);
          updateLoadingText(progress / 100);
        });

        torrent.on('done', () => {
          console.log('Torrent download complete');
          setLoadingText('Content loaded successfully');
        });
      });
    }
  };

  // Trigger blockchain info fetch and WebTorrent load
  useEffect(() => {
    fetchContractDetails();
  }, []);

  useEffect(() => {
    const domain = "example.com"; // Replace with actual domain
    const path = "path/to/content"; // Replace with actual path
    if (contractAddress && contractABI) {
      fetchMagnetLinks(domain, path);
    }
  }, [contractAddress, contractABI]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-web3-dark">
      {/* Background particle network */}
      <ParticleNetwork progress={progress} />
      
      {/* Loading progress text */}
      <div className="w-full space-y-6">
        <div className="text-center">
          <h2 className="font-mono text-web3-highlight font-medium mb-2">
            {Math.floor(progress * 100)}%
          </h2>
          <p className="text-white/80 text-sm font-mono">
            {loadingText}
          </p>
        </div>
        
        {/* Progress bar */}
        <Progress value={progress * 100} className="h-1 bg-web3-dark/50">
          <div 
            className="h-full bg-gradient-to-r from-web3-primary to-web3-light rounded-full"
            style={{ width: `${progress * 100}%` }}
          />
        </Progress>
        
        {/* Display Magnet Links with their download progress */}
        <div className="text-center mt-4">
          <h3 className="font-bold text-white">Magnet Links:</h3>
          <ul className="text-white">
            {magnetProgress.map((magnet, index) => (
              <li key={index} className="mt-2">
                <a href={magnet.magnetLink} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  {magnet.magnetLink}
                </a>
                <div className="mt-2">
                  <Progress value={magnet.progress} className="h-1 bg-web3-dark/50">
                    <div 
                      className="h-full bg-gradient-to-r from-web3-primary to-web3-light rounded-full"
                      style={{ width: `${magnet.progress}%` }}
                    />
                  </Progress>
                  <div className="text-sm text-white/60">
                    {magnet.downloadRate.toFixed(2)} MB/s | {magnet.numPeers} peers
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LoadingPage;
