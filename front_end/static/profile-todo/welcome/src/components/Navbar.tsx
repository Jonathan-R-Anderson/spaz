
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Navbar = () => {
  return (
    <header className="w-full py-4 px-6 bg-web3-darkAlt border-b border-white/10 sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-web3-primary to-web3-accent bg-clip-text text-transparent">
            W3Stream
          </h1>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex space-x-6">
          <a href="#" className="text-web3-text hover:text-web3-primary transition-colors">
            Browse
          </a>
          <a href="#" className="text-web3-text hover:text-web3-primary transition-colors">
            Categories
          </a>
          <a href="#" className="text-web3-text hover:text-web3-primary transition-colors">
            About
          </a>
        </nav>

        {/* Search Bar */}
        <div className="relative hidden md:flex w-1/3 max-w-md">
          <Input
            type="text"
            placeholder="Search streams..."
            className="w-full bg-web3-dark/60 border-web3-accent/30 text-web3-text focus:border-web3-accent"
          />
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-0 top-0 text-web3-textMuted hover:text-web3-primary"
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-3">
          <Button variant="ghost" className="border border-white/10 hover:bg-web3-accent/20 text-web3-text hover:text-white">
            Login
          </Button>
          <Button className="bg-gradient-to-r from-web3-primary to-web3-accent hover:opacity-90 text-white">
            Sign Up
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
