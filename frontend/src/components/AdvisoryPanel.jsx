import React, { useState, useEffect } from 'react';
import { AlertTriangle, Send } from 'lucide-react';

export default function AdvisoryPanel({ village }) {
  const [advisoryData, setAdvisoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (village) {
      setLoading(true);
      setError(null);
      // Fetch live inference from backend
      fetch(`http://127.0.0.1:8000/advisory/${village.id}?language=ta`)
        .then(res => {
          if (!res.ok) throw new Error("API failed");
          return res.json();
        })
        .then(data => {
          setAdvisoryData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError("Failed to fetch live inference");
          setLoading(false);
        });
    }
  }, [village]);

  const handleSend = () => {
    setSending(true);
    fetch(`http://127.0.0.1:8000/advisory/send/${village.id}`, { method: 'POST' })
      .then(res => {
        if (!res.ok) throw new Error("Failed to send");
        return res.json();
      })
      .then(() => {
        alert(`Successfully broadcasted to all farmers in ${village.name} via Pingram WhatsApp API!`);
        setSending(false);
      })
      .catch(err => {
        alert("Error sending: " + err.message);
        setSending(false);
      });
  };

  if (!village) {
    return (
      <div className="glass-panel" style={{ padding: '24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Select a village on the map to view advisories.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h2 style={{ fontSize: '1.5rem', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '12px' }}>{village.name} Overview</h2>
      
      {loading ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Querying NASA POWER & Running Inference...</p>
        </div>
      ) : error ? (
        <p style={{ color: 'var(--alert-extreme)' }}>{error}</p>
      ) : advisoryData ? (
        <>
          <div>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Risk Assessment</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '16px', borderRadius: '12px' }}>
              <AlertTriangle color="var(--alert-extreme)" />
              <div>
                <p style={{ fontWeight: 600, color: 'var(--alert-extreme)' }}>
                  Avg Predicted Rain: {(advisoryData.forecast.predicted_rain_mm.reduce((a,b)=>a+b,0)/3).toFixed(1)}mm
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Max Extreme Prob: {(Math.max(...advisoryData.forecast.extreme_probability) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          <div style={{ flex: 1 }}>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Generated Advisory (Tamil)</h4>
            <div style={{ backgroundColor: 'rgba(255,255,255,0.5)', padding: '16px', borderRadius: '12px', boxShadow: 'var(--shadow-inset)', minHeight: '120px' }}>
              <p style={{ fontStyle: 'italic', lineHeight: 1.6 }}>{advisoryData.advisory_text}</p>
            </div>
          </div>

          <button onClick={handleSend} disabled={sending} className="btn-3d btn-primary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Send size={18} />
            {sending ? "Sending via Pingram..." : "Broadcast via Pingram"}
          </button>
        </>
      ) : null}
    </div>
  );
}
