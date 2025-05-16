
import React, { useState } from 'react';
import { Play, Pause, Volume2, Users, Share, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

const VideoPlayer = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState([70]);
  const [isLiked, setIsLiked] = useState(false);

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
      {/* Stream Video Placeholder */}
      <div className="relative w-full h-0 pb-[56.25%]">
        <div className="absolute inset-0 bg-gradient-to-br from-web3-dark to-web3-darker flex items-center justify-center">
          <img 
            src="https://images.unsplash.com/photo-1605810230434-7631ac76ec81" 
            alt="Stream preview" 
            className="w-full h-full object-cover opacity-70"
          />
          
          <div className="absolute inset-0 bg-web3-darker/50" />
          
          {/* Live indicator */}
          <div className="absolute top-4 left-4 flex items-center gap-2">
            <Badge className="bg-red-600 hover:bg-red-700 px-2 py-1 text-white font-medium">LIVE</Badge>
            <Badge className="bg-web3-purple/80 hover:bg-web3-purple px-2 py-0.5 text-xs">
              <Users className="h-3 w-3 mr-1" />
              5.2K
            </Badge>
          </div>
        </div>
      </div>

      {/* Stream Controls */}
      <div className="absolute bottom-0 left-0 w-full p-4 bg-gradient-to-t from-black/90 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20 rounded-full h-8 w-8"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? 
                <Pause className="h-5 w-5" /> : 
                <Play className="h-5 w-5" />
              }
            </Button>
            
            <div className="flex items-center gap-2 max-w-[100px]">
              <Volume2 className="h-4 w-4 text-white" />
              <Slider 
                className="w-20" 
                value={volume} 
                onValueChange={setVolume} 
                max={100}
                step={1}
              />
            </div>
          </div>
          
          <div className="h-1 bg-gray-600/50 w-full max-w-[200px] md:max-w-[300px] lg:max-w-none mx-4 rounded-full overflow-hidden hidden md:block">
            <div 
              className="h-full bg-gradient-to-r from-web3-purple to-web3-accent animate-pulse-glow" 
              style={{ width: '34%' }}
            ></div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20 rounded-full h-8 w-8"
              onClick={() => setIsLiked(!isLiked)}
            >
              <Heart className={`h-5 w-5 ${isLiked ? 'fill-red-500 text-red-500' : ''}`} />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20 rounded-full h-8 w-8"
            >
              <Share className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Central Play Button for Mobile */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white hover:bg-white/10 rounded-full h-16 w-16 md:hidden"
        onClick={() => setIsPlaying(!isPlaying)}
      >
        {isPlaying ? 
          <Pause className="h-8 w-8" /> : 
          <Play className="h-8 w-8" />
        }
      </Button>
    </div>
  );
};

export default VideoPlayer;
