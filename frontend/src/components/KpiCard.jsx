import React from 'react';

export default function KpiCard({ title, value, subtext, icon: Icon, color }) {
  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
      <div style={{ backgroundColor: color, color: 'white', padding: '16px', borderRadius: '12px', boxShadow: 'var(--shadow-sm)' }}>
        <Icon size={28} />
      </div>
      <div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</p>
        <h3 style={{ fontSize: '1.8rem', marginTop: '4px', marginBottom: '4px' }}>{value}</h3>
        <p style={{ color: 'var(--accent-primary)', fontSize: '0.85rem', fontWeight: 500 }}>{subtext}</p>
      </div>
    </div>
  );
}
