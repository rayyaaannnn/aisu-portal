import React from 'react';
import SimplePage from './SimplePage';

function Logs() {
  const logs = [
    { ts: 'Today 09:24', msg: 'User john_doe updated role to state_team' },
    { ts: 'Today 08:51', msg: 'Login success for jane_smith' },
    { ts: 'Today 08:10', msg: 'Password reset request for ramesh' },
  ];

  return (
    <SimplePage title="System Logs" subtitle="Recent security and activity events">
      <section className="dashboard-section activity-section">
        <div className="activity-feed">
          {logs.map((log, idx) => (
            <div key={idx} className="activity-item">
              <div className="activity-icon" style={{ backgroundColor: '#0ea5e9', color: 'white' }}>📋</div>
              <div className="activity-content">
                <p className="activity-title">{log.msg}</p>
                <span className="activity-time">{log.ts}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </SimplePage>
  );
}

export default Logs;
