import React from 'react';
import SimplePage from './SimplePage';

function Settings() {
  return (
    <SimplePage title="Settings" subtitle="Account and portal preferences">
      <section className="dashboard-section activity-section">
        <div className="activity-item" style={{ borderBottom: 'none' }}>
          <div className="activity-icon" style={{ backgroundColor: '#6366f1', color: 'white' }}>🔒</div>
          <div className="activity-content">
            <p className="activity-title">Security</p>
            <p className="activity-description">Password resets, MFA (coming soon), session limits.</p>
          </div>
        </div>
        <div className="activity-item" style={{ borderBottom: 'none' }}>
          <div className="activity-icon" style={{ backgroundColor: '#10b981', color: 'white' }}>🌐</div>
          <div className="activity-content">
            <p className="activity-title">Locale</p>
            <p className="activity-description">Timezone, language, region preferences.</p>
          </div>
        </div>
      </section>
    </SimplePage>
  );
}

export default Settings;
