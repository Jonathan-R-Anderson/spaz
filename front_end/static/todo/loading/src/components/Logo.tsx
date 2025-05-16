
import React from 'react';

interface LogoProps {
  progress: number;
}

const Logo: React.FC<LogoProps> = ({ progress }) => {
  const fillHeight = `${progress * 100}%`;
  const hexSize = 42; // Base size for hexagons
  
  // Function to create hexagon points
  const getHexagonPoints = (x: number, y: number, size: number): string => {
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (i * 60) * Math.PI / 180;
      const pointX = x + size * Math.cos(angle);
      const pointY = y + size * Math.sin(angle);
      points.push(`${pointX},${pointY}`);
    }
    return points.join(' ');
  };

  return (
    <div className="relative w-64 h-64 mx-auto">
      {/* Rotating outer circle */}
      <div className="absolute inset-0 animate-rotate-slow opacity-30">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          <circle 
            cx="50" 
            cy="50" 
            r="48" 
            fill="none" 
            stroke="url(#outerGradient)" 
            strokeWidth="0.5" 
            strokeDasharray="4 2" 
          />
          <defs>
            <linearGradient id="outerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#9b87f5" />
              <stop offset="100%" stopColor="#33C3F0" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {/* Main logo hexagonal shape */}
      <div className="absolute inset-0 flex items-center justify-center">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Background hexagon */}
          <polygon 
            points={getHexagonPoints(50, 50, 35)} 
            fill="#1A1F2C" 
            stroke="#7E69AB" 
            strokeWidth="0.8" 
            className="drop-shadow-lg"
          />
          
          {/* Inner hexagon structure - grid of hexagons */}
          <g className="opacity-70">
            {Array.from({ length: 7 }).map((_, i) => {
              const delay = i * 0.15;
              const animationStyle = `animation: hex-appear 0.8s ease-out ${delay}s forwards; opacity: 0`;
              
              return (
                <polygon 
                  key={`hex-${i}`}
                  points={getHexagonPoints(50, 45 + i * 2, 20 - i * 2)} 
                  fill="none" 
                  stroke="#9b87f5" 
                  strokeWidth="0.3"
                  style={{ animationDelay: `${delay}s` }}
                  className="animate-hex-appear opacity-0"
                />
              );
            })}
          </g>
          
          {/* Fill effect - mask for the progress fill */}
          <defs>
            <mask id="progressMask">
              <polygon 
                points={getHexagonPoints(50, 50, 35)} 
                fill="white" 
              />
            </mask>
          </defs>
          
          {/* Progress fill */}
          <rect 
            x="0" 
            y="100" 
            width="100" 
            height="100"
            fill="url(#fillGradient)"
            mask="url(#progressMask)"
            style={{ 
              transform: `translateY(${100 - progress * 100}%)`,
              transition: 'transform 0.3s ease-out'
            }}
          />
          
          {/* Define fill gradient */}
          <defs>
            <linearGradient id="fillGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#33C3F0" />
              <stop offset="100%" stopColor="#9b87f5" />
            </linearGradient>
            
            {/* Shimmer effect */}
            <linearGradient id="shimmerGradient" x1="0%" y1="0%" x2="100%" y2="0%" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="rgba(255,255,255,0)" />
              <stop offset="50%" stopColor="rgba(255,255,255,0.3)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0)" />
            </linearGradient>
          </defs>
          
          {/* Shimmer effect overlay */}
          <rect 
            x="-100" 
            y="0" 
            width="300" 
            height="100"
            fill="url(#shimmerGradient)"
            mask="url(#progressMask)"
            className="animate-shimmer"
            style={{ 
              opacity: progress > 0.2 ? 1 : 0,
              transition: 'opacity 0.5s ease-out'
            }}
          />
          
          {/* Center dot */}
          <circle 
            cx="50" 
            cy="50" 
            r="3"
            fill="#1EAEDB" 
            className="animate-pulse-glow"
            filter="drop-shadow(0 0 3px #33C3F0)"
          />
        </svg>
      </div>
    </div>
  );
};

export default Logo;
