import React from 'react';
import SimplePage from './SimplePage';

function Districts() {
  const districts = [
    { name: 'Pune', lead: 'Anita Kulkarni', members: 120 },
    { name: 'Nagpur', lead: 'Ramesh Patil', members: 95 },
    { name: 'Mumbai', lead: 'Kiran Shah', members: 210 },
  ];

  return (
    <SimplePage title="Districts" subtitle="Your managed districts">
      <section className="dashboard-section users-section">
        <div className="recent-users-list">
          {districts.map((d) => (
            <div key={d.name} className="user-item">
              <div className="user-avatar-small">📍</div>
              <div className="user-details">
                <span className="user-username">{d.name}</span>
                <span className="user-meta">Lead: {d.lead} • Members: {d.members}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </SimplePage>
  );
}

export default Districts;
