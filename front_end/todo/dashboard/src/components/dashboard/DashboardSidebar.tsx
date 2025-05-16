
import React from 'react';
import { 
  Twitch, 
  BarChart, 
  Users, 
  Settings, 
  Wallet, 
  Activity, 
  Calendar,
  LogOut
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

const SidebarItem = ({ icon: Icon, label, active, onClick }: SidebarItemProps) => {
  return (
    <button 
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-lg w-full transition-all",
        active 
          ? "bg-web3-purple/20 text-white glow-border" 
          : "text-gray-400 hover:text-white hover:bg-white/5"
      )}
      onClick={onClick}
    >
      <Icon size={20} className={active ? "text-web3-purple" : ""} />
      <span>{label}</span>
    </button>
  );
};

interface DashboardSidebarProps {
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
}

const DashboardSidebar = ({ collapsed, setCollapsed }: DashboardSidebarProps) => {
  return (
    <aside 
      className={cn(
        "h-screen fixed left-0 top-0 z-30 flex flex-col bg-web3-dark border-r border-white/10 transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex items-center gap-3 p-4 border-b border-white/10 h-16">
        <Twitch size={28} className="text-web3-purple" />
        {!collapsed && <h1 className="text-xl font-bold text-gradient-purple">StreamFlow</h1>}
        <button 
          onClick={() => setCollapsed(!collapsed)} 
          className="ml-auto bg-white/5 p-1.5 rounded hover:bg-white/10 transition-colors"
        >
          {collapsed ? (
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8.5 4L11 6.5M11 6.5L8.5 9M11 6.5H4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 4L3.5 6.5M3.5 6.5L6 9M3.5 6.5H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </button>
      </div>
      
      <div className="flex flex-col gap-1 p-2 overflow-y-auto flex-grow">
        <SidebarItem icon={BarChart} label="Dashboard" active />
        <SidebarItem icon={Activity} label="Live Status" />
        <SidebarItem icon={Users} label="Audience" />
        <SidebarItem icon={Wallet} label="Earnings" />
        <SidebarItem icon={Calendar} label="Schedule" />
        <SidebarItem icon={Settings} label="Settings" />
      </div>
      
      <div className="p-2 border-t border-white/10">
        <SidebarItem icon={LogOut} label="Logout" />
      </div>
    </aside>
  );
};

export default DashboardSidebar;
