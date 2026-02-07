import React from 'react';
import SimplePage from './SimplePage';

function Help() {
  return (
    <SimplePage title="Help Center" subtitle="Guides and support">
      <section className="dashboard-section users-section">
        <p className="activity-description">For assistance, email support@aisu.org or call +91-800-123-4567.</p>
        <p className="activity-description" style={{ marginTop: '12px' }}>FAQ and playbooks coming soon.</p>
      </section>
    </SimplePage>
  );
}

export default Help;
