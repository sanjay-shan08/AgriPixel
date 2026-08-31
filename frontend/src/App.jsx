import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import WeatherMap from './components/WeatherMap'
import AdvisoryPanel from './components/AdvisoryPanel'

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

        <div className="dashboard-row">
          <WeatherMap onVillageClick={setSelectedVillage} />
          <AdvisoryPanel village={selectedVillage} />
        </div>
        
        <div style={{ height: '50px' }}></div>
      </div>
    </div>
  )
}

export default App
