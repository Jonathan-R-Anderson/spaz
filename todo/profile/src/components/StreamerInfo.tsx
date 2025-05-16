
import React from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Heart, CircleDollarSign, Bitcoin } from 'lucide-react';

interface StreamerInfoProps {
  name?: string;
  title?: string;
  game?: string;
  tags?: string[];
}

const StreamerInfo: React.FC<StreamerInfoProps> = ({
  name = "CryptoNova",
  title = "Building a new NFT collection! Join the whitelist 🚀",
  game = "NFT Studio",
  tags = ["NFT", "Ethereum", "Web3", "Crypto"],
}) => {
  return (
    <div className="web3-card p-4">
      <div className="flex items-start justify-between mb-4">
        <div className="flex">
          <Avatar className="h-14 w-14 rounded-full border-2 border-web3-purple/50 mr-3">
            <AvatarImage src="" alt={name} />
            <AvatarFallback className="bg-web3-purple/20 text-white font-bold">
              {name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          
          <div>
            <div className="flex items-center">
              <h2 className="text-white font-bold text-lg">{name}</h2>
              <Badge className="ml-2 bg-web3-purple/20 text-web3-purple-light border border-web3-purple/30 px-1.5">
                <Bitcoin className="h-3 w-3 mr-1" />
                Verified
              </Badge>
            </div>
            <h3 className="text-white font-medium">{title}</h3>
            <div className="text-gray-400 text-sm mt-1">{game}</div>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button className="text-white bg-web3-purple hover:bg-web3-purple-light gap-1">
            <Heart className="h-4 w-4" />
            Follow
          </Button>
          <Button variant="outline" className="text-white border-web3-purple/50 hover:bg-web3-purple/10 gap-1">
            <CircleDollarSign className="h-4 w-4" />
            Subscribe
          </Button>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mt-3">
        {tags.map((tag) => (
          <Badge 
            key={tag} 
            variant="secondary" 
            className="bg-web3-dark border border-web3-purple/20 text-gray-300 hover:bg-web3-purple/10"
          >
            {tag}
          </Badge>
        ))}
      </div>
      
      <div className="mt-4 border-t border-web3-purple/10 pt-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <div className="text-gray-400">
              <span className="text-white font-medium">352K</span> followers
            </div>
            <div className="text-gray-400">
              <span className="text-white font-medium">1.2M</span> views
            </div>
          </div>
          <div className="flex items-center gap-1 text-web3-purple">
            <Bitcoin className="h-4 w-4" />
            <span className="font-medium">Earn 0.005 ETH per watch hour</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreamerInfo;
