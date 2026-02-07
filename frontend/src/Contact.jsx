import React from 'react';
import SimplePage from './SimplePage';

function Contact() {
  const contacts = [
    { label: 'IT Support', value: 'it-support@aisu.org', icon: '🛠️' },
    { label: 'Security', value: 'security@aisu.org', icon: '🔒' },
    { label: 'Operations', value: 'ops@aisu.org', icon: '🏢' },
  ];

  return (
    <SimplePage title="Contact" subtitle="Reach the right team">
      <section className="dashboard-section users-section">
        {contacts.map((c) => (
          <div key={c.label} className="activity-item" style={{ borderBottom: 'none' }}>
            <div className="activity-icon" style={{ backgroundColor: '#0ea5e9', color: 'white' }}>{c.icon}</div>
            <div className="activity-content">
              <p className="activity-title">{c.label}</p>
              <p className="activity-description">{c.value}</p>
            </div>
          </div>
        ))}
      </section>
    </SimplePage>
  );
}

export default Contact;
