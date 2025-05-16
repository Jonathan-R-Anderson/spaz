
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Bitcoin } from 'lucide-react';

interface ChatMessage {
  id: number;
  username: string;
  message: string;
  avatar?: string;
  isSubscriber?: boolean;
  isVIP?: boolean;
  tokenTip?: number;
}

const SAMPLE_MESSAGES: ChatMessage[] = [
  { 
    id: 1, 
    username: "0xMetaMask", 
    message: "Loving the new token design! 🔥",
    isVIP: true,
  },
  { 
    id: 2, 
    username: "cryptoPunk", 
    message: "When is the drop happening?",
    isSubscriber: true,
  },
  { 
    id: 3, 
    username: "ethTrader", 
    message: "Just minted my first NFT from your collection!",
    tokenTip: 5,
  },
  { 
    id: 4, 
    username: "blockchainDev", 
    message: "The smart contract looks clean. Did you audit it?",
    isSubscriber: true,
  },
  { 
    id: 5, 
    username: "NFTcollector", 
    message: "These designs are 🔥 Can't wait to add them to my collection",
  },
  { 
    id: 6, 
    username: "0xWallet", 
    message: "Joined the whitelist! The roadmap looks promising",
    isVIP: true,
    tokenTip: 10,
  },
  { 
    id: 7, 
    username: "defiExplorer", 
    message: "Will there be staking rewards for holding the NFTs?",
  },
  { 
    id: 8, 
    username: "tokenMaster", 
    message: "These animations are smooth. What software do you use?",
    isSubscriber: true,
  }
];

const StreamChat = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(SAMPLE_MESSAGES);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    const newMessage: ChatMessage = {
      id: Date.now(),
      username: "You",
      message: message.trim(),
      isSubscriber: true,
    };
    
    setMessages([...messages, newMessage]);
    setMessage("");
  };

  return (
    <div className="web3-card flex flex-col h-full">
      <div className="bg-web3-dark border-b border-web3-purple/20 p-3">
        <h3 className="text-white font-medium">Stream Chat</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-3" style={{ maxHeight: "calc(100vh - 300px)" }}>
        {messages.map((msg) => (
          <div key={msg.id} className="flex items-start gap-2 group hover:bg-web3-purple/5 p-1 rounded-md">
            <Avatar className="h-7 w-7 rounded-full">
              <AvatarImage src={msg.avatar} />
              <AvatarFallback className={`text-xs font-bold ${
                msg.isVIP ? 'bg-web3-purple/30 text-web3-purple-light' : 
                msg.isSubscriber ? 'bg-web3-dark/80 text-gray-300' : 
                'bg-gray-700 text-gray-300'
              }`}>
                {msg.username.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            
            <div>
              <div className="flex items-center gap-1">
                <span className={`text-sm font-medium ${
                  msg.isVIP ? 'text-web3-purple-light' : 
                  msg.isSubscriber ? 'text-green-400' : 
                  'text-gray-300'
                }`}>
                  {msg.username}
                </span>
                
                {msg.isVIP && (
                  <Badge className="px-1 py-0 text-[10px] bg-web3-purple/20 text-web3-purple-light border border-web3-purple/30">
                    VIP
                  </Badge>
                )}
                
                {msg.tokenTip && (
                  <Badge className="px-1 py-0 text-[10px] bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center">
                    <Bitcoin className="h-2 w-2 mr-0.5" />
                    {msg.tokenTip}
                  </Badge>
                )}
              </div>
              
              <p className="text-gray-300 text-sm">
                {msg.message}
              </p>
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-3 border-t border-web3-purple/20">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Send a message"
            className="web3-input text-sm"
          />
          <Button type="submit" className="bg-web3-purple hover:bg-web3-purple-light text-white">
            Chat
          </Button>
        </form>
      </div>
    </div>
  );
};

export default StreamChat;
