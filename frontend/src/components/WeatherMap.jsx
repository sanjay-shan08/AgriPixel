import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Circle, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

export default function WeatherMap({ onVillageClick }) {
  const [isDownscaled, setIsDownscaled] = useState(true);
  const [villages, setVillages] = useState([]);
  const [downscaling, setDownscaling] = useState(false);
  
  // Center of Tamil Nadu roughly
  const center = [10.5, 77.5];

  useEffect(() => {
    fetch('http://127.0.0.1:8000/villages/')
      .then(res => res.json())
      .then(data => setVillages(data))
      .catch(err => console.error("Error fetching villages:", err));
  }, []);
  
  const handleMapClick = (latlng) => {
    // Switch to downscaled mode if they aren't already
    if (!isDownscaled) setIsDownscaled(true);
    
    setDownscaling(true);
    
    fetch('http://127.0.0.1:8000/downscale', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat: latlng.lat, lon: latlng.lng })
    })
    .then(res => {
      if (!res.ok) throw new Error("Failed to downscale");
      return res.json();
    })
    .then(newGrid => {
      // Append the new 25 points to our map
      setVillages(prev => [...prev, ...newGrid]);
      setDownscaling(false);
    })
    .catch(err => {
      console.error(err);
      setDownscaling(false);
    });
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem' }}>Spatial Downscaling Engine</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Click ANYWHERE on the map to generate a live 5km downscaled grid!
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {downscaling && <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>Downscaling Region...</span>}
          <button 
            className="btn-3d" 
            onClick={() => setIsDownscaled(!isDownscaled)}
            style={{ backgroundColor: isDownscaled ? 'var(--accent-primary)' : 'var(--bg-card)', color: isDownscaled ? 'white' : 'var(--text-primary)' }}
          >
            {isDownscaled ? 'Panchayat Level (5km)' : 'IMD Block Level (30km)'}
          </button>
        </div>
      </div>
      
      <div style={{ flex: 1, borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.5)', boxShadow: 'var(--shadow-inset)' }}>
        <MapContainer center={center} zoom={7} style={{ height: '100%', width: '100%', cursor: 'crosshair' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <MapClickHandler onMapClick={handleMapClick} />
          
          {isDownscaled ? (
            // DOWNSCALED MODE
            villages.map(v => (
              <Circle 
                key={v.id}
                center={[v.latitude, v.longitude]} 
                radius={2500} 
                pathOptions={{ 
                  color: 'var(--accent-secondary)', 
                  fillColor: 'var(--accent-secondary)', 
                  fillOpacity: 0.6,
                  weight: 1
                }} 
                eventHandlers={{ 
                  click: (e) => {
                    // Prevent the map click event from firing when clicking a village
                    e.originalEvent.stopPropagation();
                    onVillageClick({id: v.id, name: v.name});
                  } 
                }} 
              >
                <Popup>{v.name} (Click for localized inference)</Popup>
              </Circle>
            ))
          ) : (
            // COARSE MODE (Generic demo circles for standard IMD visualization)
            <>
               <Circle center={[11.0168, 76.9558]} radius={30000} pathOptions={{ color: 'var(--alert-extreme)', fillColor: 'var(--alert-extreme)', fillOpacity: 0.3 }} />
               <Circle center={[9.9252, 78.1198]} radius={30000} pathOptions={{ color: 'var(--alert-warn)', fillColor: 'var(--alert-warn)', fillOpacity: 0.3 }} />
               <Circle center={[13.0827, 80.2707]} radius={30000} pathOptions={{ color: 'var(--accent-primary)', fillColor: 'var(--accent-primary)', fillOpacity: 0.3 }} />
            </>
          )}
        </MapContainer>
      </div>
    </div>
  );
}
