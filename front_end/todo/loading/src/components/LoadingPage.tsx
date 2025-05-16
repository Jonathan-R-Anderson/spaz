
import React, { useState, useEffect, useCallback } from 'react';
import { initScrollJack } from '../utils/scrollJack';
import Logo from './Logo';
import ParticleNetwork from './ParticleNetwork';
import { Progress } from "@/components/ui/progress";

interface LoadingPageProps {
  onComplete: () => void;
  duration?: number;
}

const LoadingPage: React.FC<LoadingPageProps> = ({ 
  onComplete, 
  duration = 6000 
}) => {
  const [progress, setProgress] = useState(0);
  const [loadingText, setLoadingText] = useState('Initializing blockchain connection...');
  
  const updateLoadingText = useCallback((prog: number) => {
    if (prog < 0.2) {
      setLoadingText('Initializing blockchain connection...');
    } else if (prog < 0.4) {
      setLoadingText('Establishing peer connection...');
    } else if (prog < 0.6) {
      setLoadingText('Fetching block headers...');
    } else if (prog < 0.8) {
      setLoadingText('Verifying smart contracts...');
    } else if (prog < 0.95) {
      setLoadingText('Loading decentralized content...');
    } else {
      setLoadingText('Connection established');
    }
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
    // Initialize scroll jacking
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-web3-dark">
      {/* Background particle network */}
      <ParticleNetwork progress={progress} />
      
      {/* Hexagon grid background */}
      <div className="absolute inset-0 z-0 opacity-10">
        <div className="w-full h-full grid grid-cols-12 gap-4 p-4">
          {Array.from({ length: 72 }).map((_, i) => (
            <div 
              key={i} 
              className="aspect-square relative"
              style={{
                opacity: Math.random() * 0.3 + 0.1,
                animationDelay: `${Math.random() * 2}s`,
              }}
            >
              <div className="absolute inset-0 border border-web3-secondary/20 rotate-45"></div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="container relative z-10 px-4 py-8 flex flex-col items-center justify-center max-w-md">
        {/* Logo component with fill animation */}
        <div className="mb-12">
          <Logo progress={progress} />
        </div>
        
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
          
          {/* Scroll instruction - fades out as progress increases */}
          <div 
            className="flex flex-col items-center justify-center text-xs text-white/60 transition-opacity duration-300"
            style={{ opacity: Math.max(0, 1 - progress * 2) }}
          >
            <p>Scroll to accelerate loading</p>
            <span className="mt-1 animate-bounce">↓</span>
          </div>
        </div>
      </div>
      
      {/* Animated corner decorations */}
      <div className="absolute top-0 left-0 p-4 opacity-70">
        <div className="w-20 h-20 border-l-2 border-t-2 border-web3-primary animate-pulse-glow"></div>
      </div>
      <div className="absolute bottom-0 right-0 p-4 opacity-70">
        <div className="w-20 h-20 border-r-2 border-b-2 border-web3-secondary animate-pulse-glow"></div>
      </div>
    </div>
  );
};

export default LoadingPage;
