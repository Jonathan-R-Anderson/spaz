
import React from 'react';
import { cn } from '@/lib/utils';
import { Wallet, ArrowUpRight } from 'lucide-react';

interface WalletCardProps {
  balance: string;
  address: string;
  className?: string;
}

const WalletCard = ({ balance, address, className }: WalletCardProps) => {
  return (
    <div className={cn("glass-card rounded-xl overflow-hidden", className)}>
      <div className="p-4 bg-gradient-to-r from-web3-dark to-web3-charcoal">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Wallet Balance</span>
          <Wallet size={18} className="text-web3-purple" />
        </div>
        <div className="text-2xl font-bold mb-1 text-gradient-purple">{balance}</div>
        <div className="flex items-center text-xs text-gray-400">
          <span className="truncate max-w-[180px]">{address}</span>
          <button className="ml-2 p-1 hover:bg-white/10 rounded-full">
            <ArrowUpRight size={12} />
          </button>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-medium mb-3">Recent Transactions</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg">
            <div>
              <div className="text-sm">Donation Payout</div>
              <div className="text-xs text-gray-400">2 hours ago</div>
            </div>
            <div className="text-green-400">+0.045 ETH</div>
          </div>
          <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg">
            <div>
              <div className="text-sm">Subscription Revenue</div>
              <div className="text-xs text-gray-400">Yesterday</div>
            </div>
            <div className="text-green-400">+0.125 ETH</div>
          </div>
          <div className="flex items-center justify-between bg-white/5 p-2 rounded-lg">
            <div>
              <div className="text-sm">Platform Fee</div>
              <div className="text-xs text-gray-400">3 days ago</div>
            </div>
            <div className="text-red-400">-0.008 ETH</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletCard;
