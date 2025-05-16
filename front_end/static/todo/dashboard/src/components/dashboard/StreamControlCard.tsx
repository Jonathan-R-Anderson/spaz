
import React from 'react';
import { cn } from '@/lib/utils';

interface StreamControlCardProps {
  isLive: boolean;
  onToggleStream: () => void;
  uptime?: string;
  className?: string;
}

const StreamControlCard = ({ isLive, onToggleStream, uptime, className }: StreamControlCardProps) => {
  return (
    <div className={cn("glass-card rounded-xl p-4", className)}>
      <h3 className="text-lg font-medium mb-4">Stream Control</h3>
      
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-3 h-3 rounded-full",
            isLive ? "bg-green-500 animate-pulse" : "bg-gray-500"
          )} />
          <span>{isLive ? "Live" : "Offline"}</span>
        </div>
        {isLive && uptime && (
          <span className="text-sm text-gray-400">Uptime: {uptime}</span>
        )}
      </div>
      
      <button
        className={cn(
          "w-full py-3 rounded-lg font-medium transition-all",
          isLive 
            ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" 
            : "bg-green-500/20 text-green-400 hover:bg-green-500/30"
        )}
        onClick={onToggleStream}
      >
        {isLive ? "End Stream" : "Start Stream"}
      </button>
      
      <div className="grid grid-cols-2 gap-3 mt-4">
        <button className="bg-white/5 hover:bg-white/10 transition-colors p-3 rounded-lg">
          Settings
        </button>
        <button className="bg-white/5 hover:bg-white/10 transition-colors p-3 rounded-lg">
          Stream Info
        </button>
      </div>
    </div>
  );
};

export default StreamControlCard;
