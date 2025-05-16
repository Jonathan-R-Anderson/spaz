
import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Users } from 'lucide-react';

interface StreamCardProps {
  id: number;
  title: string;
  streamer: string;
  category: string;
  viewers: number;
  thumbnail: string;
  streamerAvatar?: string;
}

const RECOMMENDED_STREAMS: StreamCardProps[] = [
  {
    id: 1,
    title: "Exploring DeFi protocols & yield farming strategies",
    streamer: "DeFi_Wizard",
    category: "Crypto Finance",
    viewers: 1245,
    thumbnail: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5",
  },
  {
    id: 2,
    title: "Building smart contracts for NFT marketplace",
    streamer: "BlockchainBuidler",
    category: "Development",
    viewers: 872,
    thumbnail: "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7",
  },
  {
    id: 3,
    title: "Live NFT drawing & minting session",
    streamer: "CryptoArtist",
    category: "NFT Creation",
    viewers: 3102,
    thumbnail: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e",
  },
  {
    id: 4,
    title: "Trading analysis: ETH and BTC patterns",
    streamer: "TokenTrader",
    category: "Trading",
    viewers: 652,
    thumbnail: "https://images.unsplash.com/photo-1518770660439-4636190af475",
  },
];

const StreamCard: React.FC<StreamCardProps> = ({ title, streamer, category, viewers, thumbnail, streamerAvatar }) => {
  return (
    <div className="web3-card group hover:-translate-y-1 transition-transform duration-300 glow-effect">
      <div className="relative h-36 overflow-hidden">
        <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
        <div className="absolute top-2 left-2">
          <Badge className="bg-red-600 text-white px-1.5 py-0.5 text-xs">LIVE</Badge>
        </div>
        <div className="absolute bottom-2 right-2">
          <Badge className="bg-black/70 text-white flex items-center gap-1 px-1.5 py-0.5 text-xs">
            <Users className="h-3 w-3" />
            {viewers.toLocaleString()}
          </Badge>
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-web3-darker to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-300"></div>
      </div>
      <div className="p-3">
        <div className="flex gap-2">
          <Avatar className="h-8 w-8 rounded-full">
            <AvatarImage src={streamerAvatar} />
            <AvatarFallback className="bg-web3-purple/20 text-white text-xs font-bold">
              {streamer.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="text-white font-medium text-sm line-clamp-1">{title}</h3>
            <p className="text-gray-400 text-xs">{streamer}</p>
            <p className="text-gray-500 text-xs">{category}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const RecommendedStreams = () => {
  return (
    <div className="w-full">
      <h2 className="text-white font-semibold text-lg mb-3">Recommended Streams</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {RECOMMENDED_STREAMS.map((stream) => (
          <StreamCard key={stream.id} {...stream} />
        ))}
      </div>
    </div>
  );
};

export default RecommendedStreams;
