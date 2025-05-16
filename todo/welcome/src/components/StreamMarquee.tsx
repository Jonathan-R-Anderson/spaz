
import { useRef } from "react";

// Mock data for trending streams
const trendingStreams = [
  {
    id: 1,
    title: "Live NFT Minting Event",
    creator: "CryptoArtist",
    viewers: 12500,
    thumbnail: "https://images.unsplash.com/photo-1639322537504-6427a16b0a28?q=80&w=300&h=170&auto=format&fit=crop"
  },
  {
    id: 2,
    title: "Blockchain Gaming Marathon",
    creator: "GameOn3",
    viewers: 8300,
    thumbnail: "https://images.unsplash.com/photo-1614680376739-414d95ff43df?q=80&w=300&h=170&auto=format&fit=crop"
  },
  {
    id: 3,
    title: "Crypto Trading Strategies",
    creator: "TraderJane",
    viewers: 7200,
    thumbnail: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=300&h=170&auto=format&fit=crop"
  },
  {
    id: 4,
    title: "Web3 Development Workshop",
    creator: "DevDAO",
    viewers: 6100,
    thumbnail: "https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=300&h=170&auto=format&fit=crop"
  },
  {
    id: 5,
    title: "Metaverse Tour & Exploration",
    creator: "Meta3xplorer",
    viewers: 5900,
    thumbnail: "https://images.unsplash.com/photo-1639762681057-408e52192e55?q=80&w=300&h=170&auto=format&fit=crop"
  },
  {
    id: 6,
    title: "DAO Governance Discussion",
    creator: "Governance3",
    viewers: 4800,
    thumbnail: "https://images.unsplash.com/photo-1639322537228-5acddb9c3dce?q=80&w=300&h=170&auto=format&fit=crop"
  },
];

const StreamMarquee = () => {
  const marqueeRef = useRef<HTMLDivElement>(null);

  return (
    <div className="w-full bg-gradient-to-r from-web3-dark/80 via-web3-darkAlt to-web3-dark/80 py-6">
      <div className="container mx-auto">
        <div className="flex items-center mb-4">
          <div className="h-2 w-2 rounded-full bg-web3-primary animate-glow mr-2"></div>
          <h2 className="text-lg font-medium text-web3-primary">TRENDING NOW</h2>
        </div>
        
        <div className="marquee-container">
          <div className="marquee-content">
            {[...trendingStreams, ...trendingStreams].map((stream, index) => (
              <div 
                key={`${stream.id}-${index}`}
                className="relative flex-shrink-0 mx-2 w-[300px] h-[170px] rounded-lg overflow-hidden group cursor-pointer glow-effect"
              >
                <img 
                  src={stream.thumbnail} 
                  alt={stream.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-3">
                  <p className="text-xs font-medium text-web3-primary">
                    {new Intl.NumberFormat().format(stream.viewers)} viewers
                  </p>
                  <h3 className="text-sm font-semibold text-white truncate">{stream.title}</h3>
                  <p className="text-xs text-web3-textMuted">{stream.creator}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreamMarquee;
