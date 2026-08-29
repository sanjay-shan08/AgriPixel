import React from 'react';
import { MessageCircle, ThumbsUp, ThumbsDown } from 'lucide-react';

export default function FeedbackFeed() {
  const feedbacks = [
    { id: 1, phone: '+91 98765 43210', msg: 'நன்றி, சரியான தகவல்.', sentiment: 'positive' },
    { id: 2, phone: '+91 87654 32109', msg: 'மழை பெய்யவில்லை.', sentiment: 'negative' },
    { id: 3, phone: '+91 76543 21098', msg: 'Advisory received on time.', sentiment: 'positive' }
  ];

  return (
    <div className="glass-panel" style={{ padding: '24px', flex: 1 }}>
      <h2 style={{ fontSize: '1.25rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <MessageCircle size={20} /> Live Farmer Feedback
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {feedbacks.map(f => (
          <div key={f.id} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', padding: '12px', backgroundColor: 'rgba(255,255,255,0.4)', borderRadius: '8px' }}>
            <div style={{ marginTop: '2px' }}>
              {f.sentiment === 'positive' ? <ThumbsUp size={16} color="var(--accent-primary)" /> : <ThumbsDown size={16} color="var(--alert-extreme)" />}
            </div>
            <div>
              <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{f.phone}</p>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>"{f.msg}"</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
