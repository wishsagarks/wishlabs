// MacbookScroll.tsx
import React from 'react';

interface MacbookScrollProps {
  title: React.ReactNode;
  badge: React.ReactNode;
  src: string;
  showGradient?: boolean;
}

const MacbookScroll: React.FC<MacbookScrollProps> = ({ title, badge, src, showGradient }) => {
  return (
    <div className="relative">
      <div className="macbook">
        {/* Macbook frame and screen */}
        <div className="macbook-screen">
          <img src={src} alt="Macbook Screen" className="object-cover" />
          {showGradient && <div className="gradient-overlay" />}
        </div>
        <div className="macbook-title">{title}</div>
        <div className="macbook-badge">{badge}</div>
      </div>
    </div>
  );
};

export default MacbookScroll;
