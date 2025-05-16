
import React from 'react';
import Navbar from '@/components/Navbar';
import HeroSection from '@/components/HeroSection';
import StreamMarquee from '@/components/StreamMarquee';
import CategorySection from '@/components/CategorySection';
import StreamGrid from '@/components/StreamGrid';
import Footer from '@/components/Footer';

const Index = () => {
  return (
    <div className="min-h-screen bg-web3-dark">
      <Navbar />
      <main>
        <HeroSection />
        <StreamMarquee />
        <CategorySection />
        <StreamGrid />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
