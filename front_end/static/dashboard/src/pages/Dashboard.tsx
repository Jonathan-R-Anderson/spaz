
import React, { useState } from 'react';
import { Twitch, Users, Clock, BarChart } from 'lucide-react';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import StatCard from '@/components/dashboard/StatCard';
import ViewerChart from '@/components/dashboard/ViewerChart';
import StreamActivityCard from '@/components/dashboard/StreamActivityCard';
import StreamControlCard from '@/components/dashboard/StreamControlCard';
import WalletCard from '@/components/dashboard/WalletCard';
import { cn } from '@/lib/utils';

// Mock data
const viewerData = [
  { time: '12:00', viewers: 120 },
  { time: '12:15', viewers: 150 },
  { time: '12:30', viewers: 190 },
  { time: '12:45', viewers: 210 },
  { time: '13:00', viewers: 260 },
  { time: '13:15', viewers: 300 },
  { time: '13:30', viewers: 320 },
  { time: '13:45', viewers: 280 },
  { time: '14:00', viewers: 250 },
  { time: '14:15', viewers: 270 },
  { time: '14:30', viewers: 290 },
];

const activityData = [
  { id: '1', type: 'subscription', username: 'cryptoFan42', timestamp: '2m ago' },
  { id: '2', type: 'donation', username: 'web3believer', amount: '0.05 ETH', timestamp: '5m ago' },
  { id: '3', type: 'follow', username: 'blockchainDev', timestamp: '12m ago' },
  { id: '4', type: 'cheer', username: 'satoshiLover', amount: '500 bits', timestamp: '18m ago' },
  { id: '5', type: 'subscription', username: 'ethereumQueen', timestamp: '25m ago' },
  { id: '6', type: 'follow', username: 'defiMaster', timestamp: '36m ago' },
  { id: '7', type: 'donation', username: 'nftCollector', amount: '0.02 ETH', timestamp: '42m ago' },
  { id: '8', type: 'cheer', username: 'tokenTrader', amount: '200 bits', timestamp: '1h ago' },
];

const Dashboard = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLive, setIsLive] = useState(true);

  return (
    <div className="min-h-screen bg-background bg-grid-pattern">
      <DashboardSidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
      
      <main 
        className={cn(
          "min-h-screen transition-all duration-300 pb-8",
          sidebarCollapsed ? "pl-16" : "pl-64"
        )}
      >
        <header className="bg-web3-dark/50 backdrop-blur-md border-b border-white/5 sticky top-0 z-20 h-16 flex items-center px-6">
          <h1 className="text-xl font-medium">Dashboard</h1>
          <div className="ml-auto flex items-center gap-4">
            <button className="glass-card p-2 rounded-full hover:bg-white/10 transition-colors">
              <span className="sr-only">Notifications</span>
              <svg width="18" height="18" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7.5 0C7.77614 0 8 0.223858 8 0.5V1.80687C10.0736 2.13511 11.6526 3.90421 11.6526 6.04673V8.02982C11.6526 8.72967 11.9728 9.39646 12.5204 9.84729L12.7365 10.0213C13.2406 10.4263 12.9525 11.25 12.3079 11.25H2.69214C2.04753 11.25 1.75944 10.4263 2.26349 10.0213L2.47965 9.84729C3.02723 9.39646 3.34737 8.72967 3.34737 8.02982V6.04673C3.34737 3.90421 4.92636 2.13511 7 1.80687V0.5C7 0.223858 7.22386 0 7.5 0ZM5.75193 12C5.77041 12.3699 5.89331 12.7224 6.10666 13.0194C6.32001 13.3164 6.61069 13.5445 6.94408 13.6737C7.27747 13.8029 7.6415 13.8284 7.99045 13.7476C8.3394 13.6667 8.65657 13.4834 8.90398 13.2222C9.15139 12.9611 9.31997 12.6335 9.38917 12.2822C9.45838 11.931 9.42566 11.5694 9.29456 11.2416C9.16347 10.9139 8.94172 10.6332 8.65467 10.4335C8.36762 10.2337 8.0308 10.1232 7.68649 10.1152L7.5 10.1147L7.31386 10.1152C6.96955 10.1232 6.63273 10.2337 6.34568 10.4335C6.05863 10.6332 5.83688 10.9139 5.70578 11.2416C5.57469 11.5694 5.54197 11.931 5.61117 12.2822C5.68038 12.6335 5.84895 12.9611 6.09637 13.2222C6.26822 13.4079 6.47199 13.5534 6.69592 13.6494C6.62062 13.4666 6.56619 13.2766 6.53374 13.0829C6.478 12.7286 6.5051 12.3635 6.6128 12.022L6.6127 12.022L6.61758 12.0088C6.65977 11.8793 6.7261 11.7651 6.81174 11.6745C6.8994 11.5817 7.00346 11.5138 7.11673 11.4757L7.12962 11.4717C7.3895 11.3813 7.68459 11.4443 7.88495 11.6362C8.08532 11.828 8.15948 12.1198 8.07516 12.3809L8.07173 12.3928C8.06097 12.4258 8.04771 12.4575 8.03213 12.4874C7.99357 12.5629 7.94593 12.6324 7.89054 12.6947C7.83516 12.7569 7.77279 12.8113 7.70524 12.8562C7.63768 12.9011 7.56578 12.936 7.49159 12.9599C7.41739 12.9837 7.34168 12.9961 7.26551 12.9969C7.18934 12.9977 7.11334 12.9868 7.03859 12.9646C6.9639 12.9425 6.89119 12.9092 6.82259 12.8657C6.75398 12.8222 6.69037 12.7691 6.63355 12.7082C6.57673 12.6472 6.52748 12.5789 6.48721 12.5046C6.44694 12.4303 6.41604 12.351 6.39544 12.269C6.37483 12.187 6.36472 12.1033 6.36544 12.0194C6.36616 11.9356 6.3777 11.8521 6.39968 11.7707C6.24317 11.8469 6.11106 11.9631 6.01827 12.1045C5.9083 12.2722 5.85354 12.4683 5.85354 12.6683C5.85354 12.8684 5.9083 13.0645 6.01827 13.2322C6.03709 13.2611 6.05677 13.2892 6.07727 13.3165C6.3271 13.6547 6.69045 13.8863 7.09614 13.9628C7.50184 14.0393 7.92138 13.9552 8.26784 13.7271C8.6143 13.499 8.85856 13.1431 8.9566 12.7396C9.05464 12.336 8.99929 11.9119 8.80074 11.55C8.60219 11.188 8.27645 10.9176 7.89402 10.7926C7.51159 10.6677 7.0981 10.697 6.73743 10.8748C6.37675 11.0526 6.09493 11.3654 5.95327 11.7453C5.84925 12.0187 5.82171 12.3152 5.87279 12.6011C5.92388 12.887 6.05178 13.1528 6.24407 13.3689C6.38183 13.5321 6.55291 13.6647 6.74536 13.7575C7.03914 13.9009 7.37127 13.9443 7.69433 13.8817C8.01739 13.8191 8.31087 13.6538 8.53188 13.4114C8.75289 13.169 8.89029 12.8621 8.92507 12.5347C8.95984 12.2074 8.8903 11.8775 8.72642 11.5944C8.56254 11.3113 8.31315 11.0905 8.01262 10.9675C7.71209 10.8444 7.37742 10.8256 7.0643 10.9142C6.75118 11.0028 6.47825 11.1941 6.28946 11.4576C6.10067 11.7211 6.00747 12.0414 6.0261 12.3655C6.04473 12.6896 6.17401 12.9967 6.3915 13.238C6.5962 13.4636 6.8701 13.6156 7.17106 13.6705C7.47201 13.7254 7.78086 13.68 8.04894 13.5425C8.31702 13.4049 8.53119 13.1829 8.65839 12.9114C8.78559 12.64 8.81756 12.3352 8.74844 12.0447C8.67931 11.7542 8.51267 11.495 8.27734 11.3062C8.042 11.1175 7.75076 11.0112 7.4547 11.0053C7.15865 10.9995 6.86442 11.0944 6.62264 11.2739C6.38086 11.4534 6.20482 11.7062 6.12517 11.9945C6.04552 12.2828 6.06567 12.5877 6.18223 12.864C6.29878 13.1402 6.50531 13.3718 6.77201 13.5244C6.77037 13.5141 6.76875 13.5038 6.76714 13.4935C6.75975 13.4432 6.75975 13.3924 6.76714 13.342C6.78755 13.1906 6.86141 13.0509 6.97617 12.9471C7.09094 12.8433 7.23909 12.7813 7.39225 12.7708C7.5454 12.7603 7.69986 12.802 7.82842 12.8886C7.95698 12.9751 8.05127 13.1015 8.09435 13.2474C8.13742 13.3933 8.12646 13.5492 8.06345 13.688C7.88962 13.9737 7.62432 14.1921 7.31396 14.3108C7.00359 14.4295 6.66497 14.4423 6.34688 14.3474C6.02879 14.2525 5.74766 14.0541 5.54244 13.7809C5.33721 13.5077 5.22008 13.174 5.20845 12.8285C5.19683 12.4831 5.29128 12.1426 5.4784 11.8568C5.66552 11.5711 5.9338 11.3557 6.24674 11.2412C6.55968 11.1266 6.9006 11.1189 7.2189 11.2191C7.5372 11.3192 7.81498 11.5226 8.01501 11.8002C8.21505 12.0778 8.32624 12.414 8.32879 12.7605C8.33134 13.107 8.22513 13.4454 8.02923 13.7269C7.83334 14.0083 7.55868 14.2168 7.24198 14.323C6.92527 14.4292 6.58402 14.4281 6.26795 14.3197C6.0348 14.2394 5.82319 14.1038 5.65193 13.9252C5.48067 13.7467 5.35512 13.5301 5.28712 13.2938C5.21912 13.0574 5.21055 12.8086 5.26212 12.568C5.3137 12.3275 5.42388 12.1028 5.58236 11.9126C5.79793 11.6517 6.09126 11.4605 6.41988 11.3658C6.74851 11.2712 7.09719 11.2774 7.42178 11.3837C7.74638 11.49 8.03173 11.6913 8.23527 11.9601C8.43881 12.2289 8.54973 12.552 8.55473 12.8857C8.55973 13.2194 8.45856 13.5458 8.26301 13.8207C8.06746 14.0955 7.78803 14.3052 7.46661 14.421C7.1452 14.5368 6.79669 14.5536 6.46508 14.4692C6.13347 14.3848 5.83584 14.2028 5.61644 13.9486C5.57892 13.9068 5.54367 13.8635 5.51075 13.8188C5.26744 13.4883 5.14966 13.0845 5.17782 12.6775C5.20599 12.2706 5.37853 11.8854 5.66935 11.5895C5.96018 11.2937 6.34931 11.1052 6.75669 11.055C7.16407 11.0048 7.57508 11.0956 7.91504 11.3114C8.25501 11.5273 8.50343 11.8538 8.61301 12.2296C8.72259 12.6054 8.68533 13.0066 8.50899 13.3589C8.33265 13.7111 8.0289 13.9909 7.65507 14.1473C7.28125 14.3037 6.86265 14.3265 6.47319 14.2111C6.08374 14.0957 5.75142 13.8497 5.53763 13.5174C5.41037 13.3248 5.32554 13.1063 5.28861 12.8776C5.25193 12.6512 5.25193 12.4196 5.28861 12.1931C5.31872 11.998 5.37793 11.8088 5.46414 11.6322C5.46414 11.6322 5.75193 12 5.75193 12Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
              </svg>
            </button>
            
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-web3-purple/20 flex items-center justify-center">
                <span className="text-sm font-medium">JD</span>
              </div>
              <span className="hidden sm:inline-block">John Doe</span>
            </div>
          </div>
        </header>
        
        <div className="px-6 pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Live Viewers"
              value="287"
              icon={<Users size={20} />}
              trend={{ value: 12, isPositive: true }}
              glowing={true}
            />
            <StatCard
              title="Total Watch Time"
              value="14,532 minutes"
              icon={<Clock size={20} />}
              trend={{ value: 8, isPositive: true }}
            />
            <StatCard
              title="New Followers"
              value="43"
              icon={<Users size={20} />}
              trend={{ value: 5, isPositive: true }}
            />
            <StatCard
              title="Channel Points Used"
              value="12,780"
              icon={<BarChart size={20} />}
              trend={{ value: 3, isPositive: false }}
            />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="lg:col-span-2">
              <ViewerChart data={viewerData} className="mb-6" />
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <StreamControlCard
                  isLive={isLive}
                  onToggleStream={() => setIsLive(!isLive)}
                  uptime="2:45:12"
                />
                <StreamActivityCard activities={activityData.slice(0, 4)} />
              </div>
            </div>
            
            <div>
              <WalletCard
                balance="2.458 ETH"
                address="0x7f5ae0c3b85b5967f1ab56ffe1516e32c9837d61"
                className="mb-6"
              />
              <StreamActivityCard 
                activities={activityData}
                className="h-[calc(100%-theme(spacing.6)-theme(spacing.52))]"
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
