
interface ScrollJackOptions {
  onProgress: (progress: number) => void;
  duration: number;
  onComplete?: () => void;
  threshold?: number;
}

export const initScrollJack = ({
  onProgress,
  duration,
  onComplete,
  threshold = 100,
}: ScrollJackOptions): (() => void) => {
  let startTime = Date.now();
  let animationFrame: number | null = null;
  let completed = false;
  let progress = 0;
  
  const htmlElement = document.documentElement;
  htmlElement.classList.add('scroll-lock');
  
  // Save initial scroll position
  const initialScrollY = window.scrollY;
  
  const handleWheel = (event: WheelEvent) => {
    event.preventDefault();
    
    // Accumulate scroll delta
    progress += event.deltaY / threshold;
    
    // Clamp progress between 0 and 1
    progress = Math.max(0, Math.min(1, progress));
    
    if (progress >= 1 && !completed) {
      completed = true;
      if (onComplete) {
        onComplete();
      }
    }
    
    onProgress(progress);
  };
  
  const animate = () => {
    const elapsed = Date.now() - startTime;
    progress = Math.min(1, elapsed / duration);
    
    onProgress(progress);
    
    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate);
    } else if (!completed) {
      completed = true;
      if (onComplete) {
        onComplete();
      }
    }
  };
  
  // Start the automatic animation
  animationFrame = requestAnimationFrame(animate);
  
  // Add wheel event listener for manual control
  window.addEventListener('wheel', handleWheel, { passive: false });
  
  // Return cleanup function
  return () => {
    if (animationFrame !== null) {
      cancelAnimationFrame(animationFrame);
    }
    window.removeEventListener('wheel', handleWheel);
    htmlElement.classList.remove('scroll-lock');
    window.scrollTo(0, initialScrollY);
  };
};
