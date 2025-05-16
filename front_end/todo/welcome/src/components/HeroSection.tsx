
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

const HeroSection = () => {
  return (
    <div className="relative">
      <div className="absolute inset-0 bg-gradient-to-b from-web3-dark via-web3-accent/10 to-web3-dark z-0"></div>
      <div className="relative z-10 py-16 container mx-auto">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-web3-primary to-web3-accent bg-clip-text text-transparent">
              Discover Web3 Content
            </span>
          </h1>
          <p className="text-lg md:text-xl text-web3-textMuted mb-8">
            Watch, create and connect with creators in the decentralized streaming platform
            of the future.
          </p>
          
          <div className="flex flex-col md:flex-row gap-4 justify-center mb-8">
            <div className="relative w-full md:w-2/3">
              <Input
                type="text"
                placeholder="Search streams, creators, or categories..."
                className="w-full py-6 px-4 bg-black/40 backdrop-blur-md border border-white/10 text-white focus-visible:ring-web3-primary focus-visible:ring-offset-2 focus-visible:ring-offset-web3-darkAlt"
              />
              <Button
                size="icon"
                className="absolute right-1 top-1 bottom-1 bg-web3-primary hover:bg-web3-accent text-white"
              >
                <Search className="h-5 w-5" />
              </Button>
            </div>
            <Button className="bg-gradient-to-r from-web3-primary to-web3-accent hover:opacity-90 text-white py-6">
              Start Watching
            </Button>
          </div>
          
          <div className="flex flex-wrap justify-center gap-2">
            <Button variant="outline" className="border-white/10 text-web3-textMuted hover:text-white hover:bg-web3-primary/20">
              NFTs
            </Button>
            <Button variant="outline" className="border-white/10 text-web3-textMuted hover:text-white hover:bg-web3-primary/20">
              Gaming
            </Button>
            <Button variant="outline" className="border-white/10 text-web3-textMuted hover:text-white hover:bg-web3-primary/20">
              Development
            </Button>
            <Button variant="outline" className="border-white/10 text-web3-textMuted hover:text-white hover:bg-web3-primary/20">
              Crypto
            </Button>
            <Button variant="outline" className="border-white/10 text-web3-textMuted hover:text-white hover:bg-web3-primary/20">
              Metaverse
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
