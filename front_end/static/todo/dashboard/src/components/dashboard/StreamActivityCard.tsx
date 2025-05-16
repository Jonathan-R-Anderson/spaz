
import React from 'react';
import { cn } from '@/lib/utils';

interface ActivityItem {
  id: string;
  type: 'subscription' | 'follow' | 'donation' | 'cheer';
  username: string;
  amount?: string | number;
  timestamp: string;
}

interface StreamActivityCardProps {
  activities: ActivityItem[];
  className?: string;
}

const StreamActivityCard = ({ activities, className }: StreamActivityCardProps) => {
  // Function to get icon based on activity type
  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'subscription':
        return (
          <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400">
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7.5 0.875C7.5 0.875 7.5 0.875 7.5 0.875C3.83172 0.875 0.875 3.83172 0.875 7.5C0.875 11.1683 3.83172 14.125 7.5 14.125C11.1683 14.125 14.125 11.1683 14.125 7.5C14.125 3.83172 11.1683 0.875 7.5 0.875Z" stroke="currentColor" strokeWidth="1.5" />
              <path d="M4.5 7.5L6.5 9.5L10.5 5.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        );
      case 'follow':
        return (
          <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7.5 1.5C7.5 1.5 7 4 5.5 5.5C4 7 1.5 7.5 1.5 7.5C1.5 7.5 4 8 5.5 9.5C7 11 7.5 13.5 7.5 13.5C7.5 13.5 8 11 9.5 9.5C11 8 13.5 7.5 13.5 7.5C13.5 7.5 11 7 9.5 5.5C8 4 7.5 1.5 7.5 1.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        );
      case 'donation':
        return (
          <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2 13.5H13M7.5 11V3.5M7.5 3.5L4.5 6.5M7.5 3.5L10.5 6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        );
      case 'cheer':
        return (
          <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-400">
            <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7.5 1.5L9.08579 5.25H13.5145L10.2245 7.5L11.5 11.25L7.5 8.75L3.5 11.25L4.77551 7.5L1.48551 5.25H5.91421L7.5 1.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        );
    }
  };

  // Function to get color based on activity type
  const getActivityColor = (type: ActivityItem['type']) => {
    switch (type) {
      case 'subscription': return 'text-green-400';
      case 'follow': return 'text-blue-400';
      case 'donation': return 'text-web3-purple';
      case 'cheer': return 'text-yellow-400';
      default: return 'text-white';
    }
  };

  return (
    <div className={cn("glass-card rounded-xl overflow-hidden", className)}>
      <div className="px-4 py-3 border-b border-white/10">
        <h3 className="font-medium text-lg">Recent Activity</h3>
      </div>
      <div className="max-h-[320px] overflow-y-auto scrollbar-none">
        {activities.map((activity) => (
          <div 
            key={activity.id}
            className="px-4 py-3 border-b border-white/5 hover:bg-white/5 transition-colors flex items-center gap-3"
          >
            {getActivityIcon(activity.type)}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="font-medium truncate">
                  <span className={cn(getActivityColor(activity.type))}>{activity.username}</span>
                  {' '}
                  {activity.type === 'subscription' && 'subscribed'}
                  {activity.type === 'follow' && 'followed'}
                  {activity.type === 'donation' && 'donated'}
                  {activity.type === 'cheer' && 'cheered'}
                  {activity.amount && ' • '}
                  {activity.amount && <span className="text-white">{activity.amount}</span>}
                </p>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-2">{activity.timestamp}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StreamActivityCard;
