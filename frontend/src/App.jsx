import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import KpiCard from './components/KpiCard'
import WeatherMap from './components/WeatherMap'
import AdvisoryPanel from './components/AdvisoryPanel'
import FeedbackFeed from './components/FeedbackFeed'
import { Users, Send, Target } from 'lucide-react'

function App() {
  const [selectedVillage, setSelectedVillage] = useState(null);

  // Implement the scroll-to-green effect
  useEffect(() => {
    const handleScroll = () => {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll <= 0) return;
      
      const scrollFraction = window.scrollY / maxScroll;
      
      // Shift background position based on scroll to simulate transitioning to green
      document.body.style.backgroundPositionY = `${scrollFraction * 100}%`;
    };
    
    window.addEventListener('scroll', handleScroll);
    // Initial call
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="app-container">
      <div style={{ position: 'fixed', left: '24px', top: '24px', bottom: '24px', zIndex: 1000 }}>
        <Sidebar />
      </div>
      
      <div className="main-content" style={{ marginLeft: '120px' }}>
        <header style={{ paddingBottom: '12px', marginTop: '12px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>AgriPixel</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Agro-Advisory Command Center</p>
        </header>

        <div className="kpi-row">
          <KpiCard title="Active Farmers" value="12,450" subtext="+2.4% this week" icon={Users} color="var(--accent-secondary)" />
          <KpiCard title="Advisories Sent" value="8,920" subtext="Today" icon={Send} color="var(--accent-primary)" />
          <KpiCard title="Forecast Accuracy" value="94.2%" subtext="Village-level downscaled" icon={Target} color="var(--alert-warn)" />
        </div>

        <div className="dashboard-row">
          <WeatherMap onVillageClick={setSelectedVillage} />
          <AdvisoryPanel village={selectedVillage} />
        </div>

        {/* Add empty space to allow scrolling to see the green transition effect */}
        <div className="dashboard-row" style={{ marginTop: '24px', minHeight: '400px' }}>
          <FeedbackFeed />
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <h2 style={{ color: 'var(--accent-primary)', fontSize: '2rem' }}>Impact Realized: Healthier Crops 🌱</h2>
          </div>
        </div>
        
        <div style={{ height: '50px' }}></div>
      </div>
    </div>
  )
}

export default App
