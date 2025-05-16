
import React from 'react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
  glowing?: boolean;
}

const StatCard = ({ title, value, icon, trend, className, glowing }: StatCardProps) => {
  return (
    <div 
      className={cn(
        "glass-card rounded-xl p-4 flex flex-col",
        glowing && "animate-glow",
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-400">{title}</span>
        <div className="text-web3-purple">{icon}</div>
      </div>
      <div className="text-2xl font-bold mb-2">{value}</div>
      
      {trend && (
        <div className="flex items-center text-sm">
          <span 
            className={cn(
              "flex items-center",
              trend.isPositive ? "text-green-400" : "text-red-400"
            )}
          >
            {trend.isPositive ? (
              <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" className="mr-1">
                <path d="M7.5 3.5L7.5 11.5M7.5 3.5L3.5 7.5M7.5 3.5L11.5 7.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" className="mr-1">
                <path d="M7.5 11.5L7.5 3.5M7.5 11.5L3.5 7.5M7.5 11.5L11.5 7.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
            {trend.value}%
          </span>
          <span className="text-gray-500 ml-1">from last stream</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
