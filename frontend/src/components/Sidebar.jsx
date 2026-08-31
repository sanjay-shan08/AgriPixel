import React from 'react';
import { LayoutDashboard, Settings } from 'lucide-react';

export default function Sidebar() {
  return (
    <div className="glass-panel" style={{ width: '80px', height: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '24px 0', gap: '32px' }}>
      <div style={{ color: 'var(--accent-primary)', padding: '12px' }}>
        <LayoutDashboard size={28} />
      </div>
      <div style={{ marginTop: 'auto', color: 'var(--text-secondary)', padding: '12px', cursor: 'pointer' }}>
        <Settings size={24} />
      </div>
    </div>
  );
}
