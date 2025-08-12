import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const SetupApi = () => {
  const [federationName, setFederationName] = useState("");
  const [systemName, setSystemName] = useState("");
  const [address, setAddress] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [result, setResult] = useState<any>(null);

  async function createFederation() {
    const res = await fetch("/federate/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        federation_name: federationName,
        name: systemName,
        address,
        public_key: publicKey,
      }),
    });
    setResult(await res.json());
  }

  async function joinFederation() {
    const res = await fetch("/federate/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        federation_id: federationName,
        name: systemName,
        address,
        public_key: publicKey,
      }),
    });
    setResult(await res.json());
  }

  async function initKdc() {
    const res = await fetch("/kerberos/init_kdc", { method: "POST" });
    setResult(await res.json());
  }

  async function createPrincipal() {
    const res = await fetch("/kerberos/create_principal", { method: "POST" });
    setResult(await res.json());
  }

  async function writeConf() {
    const res = await fetch("/kerberos/write_conf", { method: "POST" });
    setResult(await res.json());
  }

  return (
    <section className="py-20 px-6">
      <div className="container mx-auto max-w-3xl space-y-6">
        <Card className="glass-card border-primary/20">
          <CardHeader>
            <CardTitle>Federation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Federation Name or ID" value={federationName} onChange={(e) => setFederationName(e.target.value)} />
            <Input placeholder="System Name" value={systemName} onChange={(e) => setSystemName(e.target.value)} />
            <Input placeholder="Address" value={address} onChange={(e) => setAddress(e.target.value)} />
            <Input placeholder="Public Key" value={publicKey} onChange={(e) => setPublicKey(e.target.value)} />
            <div className="flex gap-2 flex-wrap">
              <Button onClick={createFederation}>Create Federation</Button>
              <Button variant="outline" onClick={joinFederation}>Join Federation</Button>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card border-primary/20">
          <CardHeader>
            <CardTitle>Kerberos</CardTitle>
          </CardHeader>
          <CardContent className="flex gap-2 flex-wrap">
            <Button onClick={initKdc}>Init KDC</Button>
            <Button onClick={createPrincipal}>Create Principal</Button>
            <Button onClick={writeConf}>Write Config</Button>
          </CardContent>
        </Card>

        {result && (
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </div>
    </section>
  );
};

export default SetupApi;

