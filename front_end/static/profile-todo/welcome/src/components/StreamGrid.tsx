
import { Button } from "@/components/ui/button";

// Mock data for live streams
const liveStreams = [
  {
    id: 1,
    title: "NFT Marketplace Review Session",
    creator: "CryptoReviewer",
    viewers: 3280,
    thumbnail: "https://images.unsplash.com/photo-1639322538074-5446d4720a5e?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 2,
    title: "Building DeFi Apps from Scratch",
    creator: "DeFiDeveloper",
    viewers: 2850,
    thumbnail: "https://images.unsplash.com/photo-1639322537570-1ac89b67795a?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 3,
    title: "Live Trading with Tokenomics",
    creator: "TokenTrader",
    viewers: 2640,
    thumbnail: "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 4,
    title: "Exploring New Web3 Games",
    creator: "GameExplorer",
    viewers: 2420,
    thumbnail: "https://images.unsplash.com/photo-1611675745374-631402d4f0a8?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 5,
    title: "Smart Contract Auditing Live",
    creator: "SecurityDAO",
    viewers: 2180,
    thumbnail: "https://images.unsplash.com/photo-1639322537504-6427a16b0a28?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 6,
    title: "Metaverse Design Workshop",
    creator: "MetaDesigner",
    viewers: 1980,
    thumbnail: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 7,
    title: "Blockchain Gaming Tournament",
    creator: "GameChained",
    viewers: 1760,
    thumbnail: "https://images.unsplash.com/photo-1614680376739-414d95ff43df?q=80&w=370&auto=format&fit=crop"
  },
  {
    id: 8,
    title: "DAO Governance Meeting",
    creator: "DAOCouncil",
    viewers: 1590,
    thumbnail: "https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=370&auto=format&fit=crop"
  },
];

const StreamGrid = () => {
  return (
    <section className="py-10">
      <div className="container mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Live Streams</h2>
          <div className="flex space-x-2">
            <Button variant="outline" className="border-web3-accent/30 text-web3-textMuted hover:text-white hover:bg-web3-accent/10">
              Newest
            </Button>
            <Button variant="outline" className="border-web3-accent/30 text-web3-textMuted hover:text-white hover:bg-web3-accent/10">
              Most Viewed
            </Button>
            <Button variant="outline" className="border-web3-accent/30 text-web3-primary hover:bg-web3-primary/10">
              Trending
            </Button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {liveStreams.map((stream) => (
            <div key={stream.id} className="rounded-lg overflow-hidden bg-web3-darkAlt border border-white/5 transition-transform hover:-translate-y-1 hover:shadow-lg hover:shadow-web3-primary/20">
              <div className="relative">
                <img
                  src={stream.thumbnail}
                  alt={stream.title}
                  className="w-full h-[220px] object-cover"
                />
                <div className="absolute top-2 left-2 bg-black/70 text-web3-primary rounded px-2 py-0.5 text-xs font-medium">
                  LIVE
                </div>
                <div className="absolute bottom-2 right-2 bg-black/70 rounded px-2 py-0.5 text-xs font-medium">
                  {new Intl.NumberFormat().format(stream.viewers)} viewers
                </div>
              </div>
              <div className="p-3">
                <h3 className="font-semibold text-white truncate">{stream.title}</h3>
                <p className="text-sm text-web3-textMuted mt-1">{stream.creator}</p>
                <div className="flex justify-between items-center mt-3">
                  <div className="flex items-center">
                    <div className="w-2 h-2 rounded-full bg-web3-primary animate-pulse mr-1"></div>
                    <span className="text-xs text-web3-textMuted">Now</span>
                  </div>
                  <Button variant="link" className="text-web3-primary text-xs p-0">Watch Now</Button>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex justify-center mt-8">
          <Button className="bg-web3-darkAlt border border-web3-primary/40 text-web3-primary hover:bg-web3-primary/20">
            Load More
          </Button>
        </div>
      </div>
    </section>
  );
};

export default StreamGrid;
