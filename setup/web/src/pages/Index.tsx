import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import ServerConfig from "@/components/ServerConfig";
import SetupApi from "@/components/SetupApi";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <ServerConfig />
      <SetupApi />
    </div>
  );
};

export default Index;
