import React from 'react';
import { AlertTriangle, Send } from 'lucide-react';

export default function AdvisoryPanel({ village }) {
  if (!village) {
    return (
      <div className="glass-panel" style={{ padding: '24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Select a village on the map to view advisories.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h2 style={{ fontSize: '1.5rem', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '12px' }}>{village} Overview</h2>
      
      <div>
        <h4 style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Risk Assessment</h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '16px', borderRadius: '12px' }}>
          <AlertTriangle color="var(--alert-extreme)" />
          <div>
            <p style={{ fontWeight: 600, color: 'var(--alert-extreme)' }}>85% Flood Risk</p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Extreme rainfall expected in next 48h.</p>
          </div>
        </div>
      </div>

      <div style={{ flex: 1 }}>
        <h4 style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Generated Advisory (Tamil)</h4>
        <div style={{ backgroundColor: 'rgba(255,255,255,0.5)', padding: '16px', borderRadius: '12px', boxShadow: 'var(--shadow-inset)', minHeight: '120px' }}>
          <p style={{ fontStyle: 'italic', lineHeight: 1.6 }}>🚨 எச்சரிக்கை: அடுத்த 48 மணி நேரத்தில் மிகக் கடுமையான மழை எதிர்பார்க்கப்படுகிறது. தயவுசெய்து விதைப்பதை தள்ளிப் போடவும்.</p>
        </div>
      </div>

      <button className="btn-3d btn-primary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
        <Send size={18} />
        Send via Pingram
      </button>
    </div>
  );
}
