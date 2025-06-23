import { useEffect, useRef } from 'react';

const BackgroundAnimation = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Animation variables
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      alpha: number;
      size: number;
    }> = [];

    const circularElements: Array<{
      x: number;
      y: number;
      radius: number;
      angle: number;
      speed: number;
      alpha: number;
    }> = [];

    // Initialize particles
    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        alpha: Math.random() * 0.5 + 0.1,
        size: Math.random() * 2 + 1
      });
    }

    // Initialize circular elements (HAL's eye inspiration)
    for (let i = 0; i < 3; i++) {
      circularElements.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 100 + 50,
        angle: 0,
        speed: 0.01 + Math.random() * 0.02,
        alpha: 0.1 + Math.random() * 0.1
      });
    }

    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw connecting lines between particles
      ctx.strokeStyle = 'rgba(220, 38, 38, 0.1)';
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 100) {
            ctx.globalAlpha = (100 - distance) / 100 * 0.3;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw and update particles
      particles.forEach(particle => {
        ctx.globalAlpha = particle.alpha;
        ctx.fillStyle = '#dc2626';
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();

        // Update particle position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Bounce off edges
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

        // Keep particles in bounds
        particle.x = Math.max(0, Math.min(canvas.width, particle.x));
        particle.y = Math.max(0, Math.min(canvas.height, particle.y));
      });

      // Draw circular elements (HAL's eye-like circles)
      circularElements.forEach(element => {
        ctx.globalAlpha = element.alpha * (0.5 + 0.5 * Math.sin(element.angle));
        ctx.strokeStyle = '#dc2626';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(element.x, element.y, element.radius, 0, Math.PI * 2);
        ctx.stroke();

        // Draw inner circle
        ctx.globalAlpha = element.alpha * 0.3;
        ctx.beginPath();
        ctx.arc(element.x, element.y, element.radius * 0.6, 0, Math.PI * 2);
        ctx.stroke();

        // Update angle for pulsing effect
        element.angle += element.speed;

        // Slowly move the circles
        element.x += Math.sin(element.angle * 0.3) * 0.2;
        element.y += Math.cos(element.angle * 0.2) * 0.2;

        // Keep circles in bounds
        if (element.x < -element.radius) element.x = canvas.width + element.radius;
        if (element.x > canvas.width + element.radius) element.x = -element.radius;
        if (element.y < -element.radius) element.y = canvas.height + element.radius;
        if (element.y > canvas.height + element.radius) element.y = -element.radius;
      });

      ctx.globalAlpha = 1;
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: 'transparent' }}
    />
  );
};

export default BackgroundAnimation;
