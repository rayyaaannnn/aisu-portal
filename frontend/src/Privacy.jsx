import React from 'react';
import SimplePage from './SimplePage';

const sections = [
  {
    title: 'What We Collect',
    body: 'Account details (name, username, role), contact info, state/district, and activity needed to operate the portal.',
  },
  {
    title: 'How We Use It',
    body: 'To manage membership, authorize access, send important notices, and improve portal security and performance.',
  },
  {
    title: 'Sharing',
    body: 'Data is shared only with authorized AISU admins/teams and required service providers; we do not sell your data.',
  },
  {
    title: 'Retention & Security',
    body: 'Data is retained while your account is active and as needed for compliance. We use reasonable safeguards; no system is 100% secure.',
  },
  {
    title: 'Your Choices',
    body: 'You may update your profile, request corrections, or ask for access removal by contacting the AISU admin team.',
  },
  {
    title: 'Cookies & Tokens',
    body: 'Session tokens/cookies are used for authentication and to keep you signed in; clearing them will sign you out.',
  },
  {
    title: 'Contact',
    body: 'For privacy questions or requests, reach out to the AISU admin team.',
  },
];

function Privacy() {
  return (
    <SimplePage title="Privacy Policy" subtitle="How AISU handles your information">
      <section className="dashboard-section users-section">
        <div className="recent-users-list">
          {sections.map((s) => (
            <div key={s.title} className="user-item" style={{ alignItems: 'flex-start' }}>
              <div className="user-avatar-small" aria-hidden>🔒</div>
              <div className="user-details">
                <span className="user-username">{s.title}</span>
                <span className="user-meta" style={{ lineHeight: 1.5 }}>{s.body}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </SimplePage>
  );
}

export default Privacy;
