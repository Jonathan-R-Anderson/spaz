
import React from 'react';
import Navbar from '@/components/Navbar';
import VideoPlayer from '@/components/VideoPlayer';
import StreamerInfo from '@/components/StreamerInfo';
import StreamChat from '@/components/StreamChat';
import RecommendedStreams from '@/components/RecommendedStreams';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col bg-web3-darker">
      <Navbar />
      
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {/* Main content (Video player and streamer info) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="web3-card overflow-hidden">
              <VideoPlayer />
            </div>
            <StreamerInfo />
          </div>
          
          {/* Chat sidebar */}
          <div className="lg:col-span-1 h-[calc(100vh-220px)] lg:min-h-[500px]">
            <StreamChat />
          </div>
        </div>
        
        {/* Recommended streams */}
        <div className="mt-8">
          <RecommendedStreams />
        </div>
      </main>
      
      {/* Web3 pattern background */}
      <div 
        className="fixed inset-0 pointer-events-none z-[-1]" 
        style={{
          backgroundSize: '40px 40px',
          backgroundImage: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 1px, transparent 1px)',
        }}
      ></div>
    </div>
  );
};

export default Index;
