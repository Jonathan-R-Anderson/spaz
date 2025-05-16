
import React, { useEffect, useRef } from 'react';

interface ParticleNetworkProps {
  progress: number;
}

const ParticleNetwork: React.FC<ParticleNetworkProps> = ({ progress }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particles = useRef<Particle[]>([]);
  
  interface Particle {
    x: number;
    y: number;
    radius: number;
    color: string;
    vx: number;
    vy: number;
    connected: boolean;
    connections: number[];
    alpha: number;
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas to full window size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create particles
    const particleCount = 50 + Math.floor(progress * 30);
    const createParticles = () => {
      particles.current = [];
      const colors = ['#9b87f5', '#7E69AB', '#33C3F0', '#1EAEDB'];
      
      for (let i = 0; i < particleCount; i++) {
        const radius = 2 + Math.random() * 3;
        particles.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: radius,
          color: colors[Math.floor(Math.random() * colors.length)],
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          connected: false,
          connections: [],
          alpha: 0.3 + Math.random() * 0.7
        });
      }
      
      // Create connections between particles
      for (let i = 0; i < particles.current.length; i++) {
        const connectionsCount = Math.floor(Math.random() * 3) + 1; // 1-3 connections per particle
        const connectedIndices = new Set<number>();
        
        for (let j = 0; j < connectionsCount; j++) {
          let targetIndex;
          do {
            targetIndex = Math.floor(Math.random() * particles.current.length);
          } while (targetIndex === i || connectedIndices.has(targetIndex));
          
          connectedIndices.add(targetIndex);
          particles.current[i].connections.push(targetIndex);
        }
      }
    };

    createParticles();

    const render = () => {
      if (!ctx || !canvas) return;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw connections first so they appear behind particles
      for (let i = 0; i < particles.current.length; i++) {
        const particle = particles.current[i];
        
        // Only draw connections for existing particles based on progress
        if (i < particleCount * progress) {
          for (let j = 0; j < particle.connections.length; j++) {
            const connectedIndex = particle.connections[j];
            
            // Only connect to particles that already exist based on progress
            if (connectedIndex < particleCount * progress) {
              const connectedParticle = particles.current[connectedIndex];
              
              // Calculate distance for opacity
              const dx = particle.x - connectedParticle.x;
              const dy = particle.y - connectedParticle.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              
              // Only connect nearby particles
              if (distance < 250) {
                const opacity = Math.max(0, 1 - (distance / 250)) * 0.5 * progress;
                
                ctx.beginPath();
                ctx.strokeStyle = `rgba(155, 135, 245, ${opacity})`;
                ctx.lineWidth = 1;
                ctx.moveTo(particle.x, particle.y);
                ctx.lineTo(connectedParticle.x, connectedParticle.y);
                ctx.stroke();
              }
            }
          }
        }
      }
      
      // Draw particles
      for (let i = 0; i < particles.current.length; i++) {
        // Only draw particles that should exist based on progress
        if (i < particleCount * progress) {
          const particle = particles.current[i];
          
          // Draw glow effect
          const gradient = ctx.createRadialGradient(
            particle.x, particle.y, 0,
            particle.x, particle.y, particle.radius * 4
          );
          gradient.addColorStop(0, `rgba(155, 135, 245, ${0.3 * particle.alpha * progress})`);
          gradient.addColorStop(1, 'rgba(155, 135, 245, 0)');
          
          ctx.beginPath();
          ctx.fillStyle = gradient;
          ctx.arc(particle.x, particle.y, particle.radius * 4, 0, Math.PI * 2);
          ctx.fill();
          
          // Draw particle
          ctx.beginPath();
          ctx.fillStyle = particle.color;
          ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
          ctx.fill();
          
          // Update position
          particle.x += particle.vx;
          particle.y += particle.vy;
          
          // Bounce off walls
          if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
          if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        }
      }
    };

    const animate = () => {
      render();
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [progress]);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed top-0 left-0 w-full h-full z-0 opacity-90"
    />
  );
};

export default ParticleNetwork;
