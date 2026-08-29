import React, { useState } from 'react';
import { MapContainer, TileLayer, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function WeatherMap({ onVillageClick }) {
  const [isDownscaled, setIsDownscaled] = useState(true);
  
  // Dummy coordinates for Tamil Nadu
  const center = [11.1271, 78.6569];
  
  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.5rem' }}>Regional Forecast Map</h2>
        <button 
          className="btn-3d" 
          onClick={() => setIsDownscaled(!isDownscaled)}
          style={{ backgroundColor: isDownscaled ? 'var(--accent-primary)' : 'var(--bg-card)', color: isDownscaled ? 'white' : 'var(--text-primary)' }}
        >
          {isDownscaled ? 'Downscaled (AgriPixel)' : 'Coarse (IMD Block)'}
        </button>
      </div>
      
      <div style={{ flex: 1, borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.5)', boxShadow: 'var(--shadow-inset)' }}>
        <MapContainer center={center} zoom={7} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/">Carto</a>'
          />
          {/* Dummy visual for downscaled vs coarse */}
          {isDownscaled ? (
            <>
               <Circle center={[13.0827, 80.2707]} radius={15000} pathOptions={{ color: 'var(--alert-extreme)', fillColor: 'var(--alert-extreme)', fillOpacity: 0.6 }} eventHandlers={{ click: () => onVillageClick('Chennai') }} />
               <Circle center={[11.0168, 76.9558]} radius={15000} pathOptions={{ color: 'var(--accent-secondary)', fillColor: 'var(--accent-secondary)', fillOpacity: 0.6 }} eventHandlers={{ click: () => onVillageClick('Coimbatore') }} />
               <Circle center={[9.9252, 78.1198]} radius={15000} pathOptions={{ color: 'var(--alert-warn)', fillColor: 'var(--alert-warn)', fillOpacity: 0.6 }} eventHandlers={{ click: () => onVillageClick('Madurai') }} />
            </>
          ) : (
            <>
               <Circle center={[12.5, 79.5]} radius={60000} pathOptions={{ color: 'var(--alert-extreme)', fillColor: 'var(--alert-extreme)', fillOpacity: 0.3 }} />
               <Circle center={[10.5, 77.5]} radius={60000} pathOptions={{ color: 'var(--accent-secondary)', fillColor: 'var(--accent-secondary)', fillOpacity: 0.3 }} />
            </>
          )}
        </MapContainer>
      </div>
    </div>
  );
}
