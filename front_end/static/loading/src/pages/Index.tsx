import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import LoadingPage from '../components/LoadingPage';
declare global {
  interface Window {
    WebTorrent: any;
  }
}

const CONTRACT_ADDRESS = '0xYourSpazMagnetStoreAddress';
const CONTRACT_ABI = [
  {
    inputs: [],
    name: 'getRecentMagnets',
    outputs: [{ internalType: 'string[]', name: '', type: 'string[]' }],
    stateMutability: 'view',
    type: 'function',
  },
];

const Index = () => {
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState<any>(null);
  const [magnets, setMagnets] = useState<string[]>([]);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const fetchBlockchainContent = () => {
    return {
      title: 'Web3 Application',
      description: 'Welcome to your decentralized application',
      blocks: [
        { id: 1, title: 'Block #14562978', hash: '0x8f7d...3e21', transactions: 142 },
        { id: 2, title: 'Block #14562979', hash: '0x9a3c...8f12', transactions: 98 },
        { id: 3, title: 'Block #14562980', hash: '0x1b7e...6d45', transactions: 127 },
      ],
    };
  };

  const fetchMagnets = async () => {
    try {
      if (!window.ethereum) throw new Error('MetaMask is not installed');
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      await provider.send('eth_requestAccounts', []);
      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      const data: string[] = await contract.getRecentMagnets();
      setMagnets(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };
  const fetchDynamicPage = async () => {
    const domain = window.location.hostname;
    const params = new URLSearchParams(window.location.search);
    const path = params.get('target') || 'index.html';
  
    try {
      const magnet = await fetch(`/api/get_magnet/${domain}`).then(res => res.text());
  
      const client = new (window as any).WebTorrent();
      client.add(magnet, torrent => {
        const file = torrent.files.find(f => f.name === path || f.name.endsWith(`/${path}`));
        if (!file) {
          console.error('❌ File not found in torrent');
          return;
        }
  
        file.getBlobURL((err, blobUrl) => {
          if (err || !blobUrl) {
            console.error('❌ Error creating blob URL', err);
            return;
          }
  
          // ✅ Hard redirect the browser to the downloaded blob
          window.location.href = blobUrl;
        });
      });
    } catch (err) {
      console.error('Torrent load failed', err);
    }
  };

  const handleLoadingComplete = async () => {
    setContent(fetchBlockchainContent());
    await fetchMagnets();
    await fetchDynamicPage();
    setLoading(false);
  };

  const MainContent = () => (
    <div className="min-h-screen bg-gradient-to-b from-web3-dark to-black py-16">
      <div className="container mx-auto px-4">
        <header className="text-center mb-16">
          <h1 className="text-4xl font-bold text-white mb-4">{content.title}</h1>
          <p className="text-lg text-white/80">{content.description}</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-16">
          {content.blocks.map((block: any) => (
            <div
              key={block.id}
              className="bg-web3-dark/40 backdrop-blur border border-web3-primary/20 rounded-lg p-6 hover:shadow-lg transition-all hover:border-web3-primary/50"
            >
              <h3 className="text-web3-highlight text-xl font-medium mb-2">{block.title}</h3>
              <p className="text-white/70 font-mono text-sm mb-2">Hash: {block.hash}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">Transactions:</span>
                <span className="font-mono text-web3-primary">{block.transactions}</span>
              </div>
            </div>
          ))}
        </div>

        <section className="max-w-3xl mx-auto text-white mb-12">
          <h2 className="text-2xl font-bold mb-4">Recent Magnet URLs</h2>
          {error && <p className="text-red-500 mb-4">Error: {error}</p>}
          <ul className="space-y-2">
            {magnets.map((magnet, index) => (
              <li key={index} className="bg-black/20 p-3 rounded break-words border border-white/10">
                {magnet}
              </li>
            ))}
            {magnets.length === 0 && !error && (
              <li className="text-white/60 italic">No magnet links found.</li>
            )}
          </ul>
        </section>

        <section className="max-w-3xl mx-auto text-white">
          <h2 className="text-2xl font-bold mb-4">Dynamic Page Content</h2>
          <div
            className="bg-black/30 p-6 rounded border border-white/10"
            dangerouslySetInnerHTML={{ __html: htmlContent }}
          />
        </section>
      </div>
    </div>
  );

  return loading ? (
    <LoadingPage onComplete={handleLoadingComplete} duration={3000} />
  ) : (
    <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
  );
  
  
};

export default Index;
