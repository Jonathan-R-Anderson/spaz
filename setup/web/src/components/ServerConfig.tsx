import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Cpu, 
  HardDrive, 
  Wifi, 
  Database, 
  Shield, 
  Zap,
  DollarSign,
  Settings
} from "lucide-react";

const ServerConfig = () => {
  const [cpuCores, setCpuCores] = useState([4]);
  const [ram, setRam] = useState([8]);
  const [storage, setStorage] = useState([100]);
  const [apiEnabled, setApiEnabled] = useState(true);
  const [sslEnabled, setSslEnabled] = useState(true);
  const [cdnEnabled, setCdnEnabled] = useState(false);

  const calculatePrice = () => {
    const basePrice = 10;
    const cpuPrice = cpuCores[0] * 5;
    const ramPrice = ram[0] * 2;
    const storagePrice = storage[0] * 0.1;
    const apiPrice = apiEnabled ? 15 : 0;
    const sslPrice = sslEnabled ? 5 : 0;
    const cdnPrice = cdnEnabled ? 20 : 0;
    
    return (basePrice + cpuPrice + ramPrice + storagePrice + apiPrice + sslPrice + cdnPrice).toFixed(2);
  };

  return (
    <section className="py-20 px-6">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Configure Your <span className="gradient-text">Dream Server</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Customize every aspect of your server before deployment. No surprises, full control.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="specs" className="space-y-6">
              <TabsList className="grid w-full grid-cols-3 glass-card">
                <TabsTrigger value="specs" className="flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  Specs
                </TabsTrigger>
                <TabsTrigger value="features" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Features
                </TabsTrigger>
                <TabsTrigger value="api" className="flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  API Config
                </TabsTrigger>
              </TabsList>

              <TabsContent value="specs" className="space-y-6">
                <Card className="glass-card border-primary/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Cpu className="w-5 h-5 text-primary" />
                      Server Specifications
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <div>
                      <Label className="text-base font-medium mb-4 block">
                        CPU Cores: {cpuCores[0]}
                      </Label>
                      <Slider
                        value={cpuCores}
                        onValueChange={setCpuCores}
                        max={16}
                        min={1}
                        step={1}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground mt-2">
                        <span>1 Core</span>
                        <span>16 Cores</span>
                      </div>
                    </div>

                    <div>
                      <Label className="text-base font-medium mb-4 block">
                        RAM: {ram[0]} GB
                      </Label>
                      <Slider
                        value={ram}
                        onValueChange={setRam}
                        max={64}
                        min={1}
                        step={1}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground mt-2">
                        <span>1 GB</span>
                        <span>64 GB</span>
                      </div>
                    </div>

                    <div>
                      <Label className="text-base font-medium mb-4 block">
                        Storage: {storage[0]} GB
                      </Label>
                      <Slider
                        value={storage}
                        onValueChange={setStorage}
                        max={1000}
                        min={10}
                        step={10}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground mt-2">
                        <span>10 GB</span>
                        <span>1 TB</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="features" className="space-y-6">
                <Card className="glass-card border-secondary/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-secondary" />
                      Advanced Features
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label className="text-base font-medium">SSL Certificate</Label>
                        <p className="text-sm text-muted-foreground">
                          Automatic HTTPS encryption for your domain
                        </p>
                      </div>
                      <Switch checked={sslEnabled} onCheckedChange={setSslEnabled} />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label className="text-base font-medium">CDN Integration</Label>
                        <p className="text-sm text-muted-foreground">
                          Global content delivery network for faster access
                        </p>
                      </div>
                      <Switch checked={cdnEnabled} onCheckedChange={setCdnEnabled} />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label className="text-base font-medium">API Gateway</Label>
                        <p className="text-sm text-muted-foreground">
                          Integrated API management and routing
                        </p>
                      </div>
                      <Switch checked={apiEnabled} onCheckedChange={setApiEnabled} />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="api" className="space-y-6">
                <Card className="glass-card border-accent/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="w-5 h-5 text-accent" />
                      API Configuration
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <Label htmlFor="api-endpoint">API Endpoint</Label>
                      <Input 
                        id="api-endpoint"
                        placeholder="https://api.example.com"
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label htmlFor="api-key">API Key</Label>
                      <Input 
                        id="api-key"
                        type="password"
                        placeholder="Your API key"
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label htmlFor="webhook-url">Webhook URL</Label>
                      <Input 
                        id="webhook-url"
                        placeholder="https://your-app.com/webhook"
                        className="mt-2"
                      />
                    </div>

                    <div className="flex gap-2 flex-wrap">
                      <Badge variant="secondary">REST API</Badge>
                      <Badge variant="secondary">GraphQL</Badge>
                      <Badge variant="secondary">WebSocket</Badge>
                      <Badge variant="secondary">gRPC</Badge>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Pricing Panel */}
          <div className="lg:col-span-1">
            <Card className="glass-card border-primary/20 sticky top-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-primary" />
                  Estimated Cost
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center">
                  <div className="text-4xl font-bold gradient-text mb-2">
                    ${calculatePrice()}
                  </div>
                  <p className="text-muted-foreground">per month</p>
                </div>

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span>Base Server</span>
                    <span>$10.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span>CPU ({cpuCores[0]} cores)</span>
                    <span>${(cpuCores[0] * 5).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>RAM ({ram[0]} GB)</span>
                    <span>${(ram[0] * 2).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Storage ({storage[0]} GB)</span>
                    <span>${(storage[0] * 0.1).toFixed(2)}</span>
                  </div>
                  {apiEnabled && (
                    <div className="flex justify-between">
                      <span>API Gateway</span>
                      <span>$15.00</span>
                    </div>
                  )}
                  {sslEnabled && (
                    <div className="flex justify-between">
                      <span>SSL Certificate</span>
                      <span>$5.00</span>
                    </div>
                  )}
                  {cdnEnabled && (
                    <div className="flex justify-between">
                      <span>CDN</span>
                      <span>$20.00</span>
                    </div>
                  )}
                </div>

                <Button variant="hero" size="lg" className="w-full">
                  Deploy Server
                </Button>

                <Button variant="outline" size="lg" className="w-full">
                  Save Configuration
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ServerConfig;