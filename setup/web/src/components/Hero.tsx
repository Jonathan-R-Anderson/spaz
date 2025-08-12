import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Server, Zap, Shield, Globe } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-background/50 to-background/80" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 z-10 grid-bg opacity-20" />

      {/* Hero Content */}
      <div className="relative z-20 container mx-auto px-6 text-center">
        <div className="max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 glass-card px-4 py-2 rounded-full mb-8">
            <Zap className="w-4 h-4 text-accent" />
            <span className="text-sm text-muted-foreground">Next-Gen Infrastructure</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Deploy Web3 Servers
            <br />
            <span className="gradient-text">Before They Exist</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto">
            Configure, customize, and deploy your web servers with integrated APIs 
            in the decentralized cloud. No infrastructure headaches, just pure performance.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button variant="hero" size="lg" className="text-lg px-8 py-6">
              <Server className="w-5 h-5" />
              Start Configuring
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-6">
              <Globe className="w-5 h-5" />
              View Demo
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <Card className="glass-card p-6 text-center border-primary/20">
              <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mx-auto mb-4 glow-primary">
                <Server className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Pre-Deploy Config</h3>
              <p className="text-muted-foreground">Set up your server specs, APIs, and features before deployment</p>
            </Card>

            <Card className="glass-card p-6 text-center border-secondary/20">
              <div className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center mx-auto mb-4 glow-hover">
                <Zap className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
              <p className="text-muted-foreground">Deploy instantly with our optimized infrastructure pipeline</p>
            </Card>

            <Card className="glass-card p-6 text-center border-accent/20">
              <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Secure by Design</h3>
              <p className="text-muted-foreground">Enterprise-grade security with Web3 decentralization</p>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
