
import React from 'react';
import { Search, Bitcoin, Twitch, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

const Navbar = () => {
  return (
    <header className="w-full bg-web3-darker border-b border-web3-purple/20 py-3 px-4">
      <div className="flex items-center justify-between w-full max-w-[1600px] mx-auto">
        <div className="flex items-center gap-2">
          <div className="flex items-center">
            <Twitch className="text-web3-purple h-8 w-8" />
            <span className="text-white font-bold text-xl ml-1">Web3Cast</span>
          </div>
          <Button variant="ghost" className="text-gray-300 hover:text-white hover:bg-web3-dark">
            Browse
          </Button>
          <Button variant="ghost" className="text-gray-300 hover:text-white hover:bg-web3-dark">
            <Bitcoin className="h-4 w-4 mr-1" />
            NFT Drops
          </Button>
        </div>

        <div className="relative max-w-md w-full hidden md:block">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search streams, games, or creators"
            className="pl-9 bg-web3-dark border-web3-purple/20 focus-visible:ring-web3-purple/50 text-sm"
          />
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="text-gray-300 hover:text-white hover:bg-web3-dark">
            <Search className="h-5 w-5 md:hidden" />
          </Button>
          <Button className="bg-web3-purple hover:bg-web3-purple-light text-white">
            Connect Wallet
          </Button>
          <Avatar className="h-8 w-8">
            <AvatarImage src="" />
            <AvatarFallback className="bg-web3-purple/20">
              <User className="h-4 w-4 text-web3-purple-light" />
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
