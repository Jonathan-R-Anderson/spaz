
import React, { useState, useEffect } from 'react';
import LoadingPage from '../components/LoadingPage';

const Index = () => {
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState<any>(null);

  // Function to simulate fetching content from blockchain
  const fetchBlockchainContent = () => {
    // This would be replaced with actual blockchain data fetching
    return {
      title: "Web3 Application",
      description: "Welcome to your decentralized application",
      blocks: [
        { id: 1, title: "Block #14562978", hash: "0x8f7d...3e21", transactions: 142 },
        { id: 2, title: "Block #14562979", hash: "0x9a3c...8f12", transactions: 98 },
        { id: 3, title: "Block #14562980", hash: "0x1b7e...6d45", transactions: 127 },
      ]
    };
  };

  const handleLoadingComplete = () => {
    // Simulate content loaded from blockchain
    const blockchainContent = fetchBlockchainContent();
    setContent(blockchainContent);
    setLoading(false);
  };

  // This component would normally contain your actual application content
  const MainContent = () => (
    <div className="min-h-screen bg-gradient-to-b from-web3-dark to-black py-16">
      <div className="container mx-auto px-4">
        <header className="text-center mb-16">
          <h1 className="text-4xl font-bold text-white mb-4">{content.title}</h1>
          <p className="text-lg text-white/80">{content.description}</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
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
      </div>
    </div>
  );

  return loading ? (
    <LoadingPage onComplete={handleLoadingComplete} duration={8000} />
  ) : (
    <MainContent />
  );
};

export default Index;
