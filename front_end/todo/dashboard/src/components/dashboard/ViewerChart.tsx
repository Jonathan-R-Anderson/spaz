
import React from 'react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface ViewerChartProps {
  data: { time: string; viewers: number }[];
  className?: string;
}

const ViewerChart = ({ data, className }: ViewerChartProps) => {
  return (
    <div className={`glass-card rounded-xl p-4 ${className}`}>
      <h3 className="text-lg font-medium mb-4">Current Stream Viewers</h3>
      <div className="h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorViewers" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#9b87f5" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#9b87f5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="time" 
              axisLine={false}
              tickLine={false}
              tickMargin={10}
              tick={{ fill: '#8E9196', fontSize: 12 }}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tickMargin={10}
              tick={{ fill: '#8E9196', fontSize: 12 }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(26, 31, 44, 0.9)',
                borderColor: 'rgba(155, 135, 245, 0.3)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
              }}
              itemStyle={{ color: '#fff' }}
              labelStyle={{ color: '#8E9196' }}
            />
            <Area 
              type="monotone" 
              dataKey="viewers" 
              stroke="#9b87f5" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorViewers)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ViewerChart;
