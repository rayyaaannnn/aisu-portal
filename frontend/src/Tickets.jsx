import React from 'react';
import SimplePage from './SimplePage';

function Tickets() {
  const tickets = [
    { id: 'TCK-1024', title: 'Email service lag', status: 'Open', priority: 'High' },
    { id: 'TCK-1025', title: 'Member import CSV', status: 'In Progress', priority: 'Medium' },
    { id: 'TCK-1026', title: 'Reset MFA device', status: 'Pending', priority: 'Low' },
  ];

  return (
    <SimplePage title="Support Tickets" subtitle="Track and triage issues">
      <section className="dashboard-section">
        <div className="activity-section">
          {tickets.map((t) => (
            <div key={t.id} className="activity-item" style={{ alignItems: 'center' }}>
              <div className="activity-icon" style={{ backgroundColor: '#2563eb', color: 'white' }}>🎫</div>
              <div className="activity-content">
                <p className="activity-title">{t.id} · {t.title}</p>
                <p className="activity-description">Priority: {t.priority}</p>
              </div>
              <span className="activity-time">{t.status}</span>
            </div>
          ))}
        </div>
      </section>
    </SimplePage>
  );
}

export default Tickets;
