import React from 'react';
import SimplePage from './SimplePage';

function Activity() {
  const feed = [
    { title: 'New district added', desc: 'District Pune registered', time: '1h ago', icon: '🆕', color: '#10b981' },
    { title: 'Role change', desc: 'Anita promoted to State Lead', time: '3h ago', icon: '⚙️', color: '#f59e0b' },
    { title: 'Event update', desc: 'Annual meet date confirmed', time: 'Yesterday', icon: '📅', color: '#6366f1' },
  ];

  return (
    <SimplePage title="Activity" subtitle="Recent changes across AISU">
      <section className="dashboard-section activity-section">
        <div className="activity-feed">
          {feed.map((item, idx) => (
            <div key={idx} className="activity-item">
              <div className="activity-icon" style={{ backgroundColor: item.color, color: 'white' }}>{item.icon}</div>
              <div className="activity-content">
                <p className="activity-title">{item.title}</p>
                <p className="activity-description">{item.desc}</p>
                <span className="activity-time">{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </SimplePage>
  );
}

export default Activity;
