import React from 'react';
import SimplePage from './SimplePage';

const sections = [
  {
    title: 'Acceptance of Terms',
    body: 'By accessing or using the AISU Portal you agree to these Terms & Conditions. If you do not agree, please refrain from using the portal.',
  },
  {
    title: 'Authorized Use',
    body: 'Use the portal only for AISU-related work, comply with applicable laws, and do not share credentials or misuse data.',
  },
  {
    title: 'Accounts & Security',
    body: 'Keep your login details confidential. Notify admins immediately of any unauthorized access or suspected breach.',
  },
  {
    title: 'Content & Data',
    body: 'Information you submit must be accurate and must not infringe third-party rights. AISU may review or remove content that violates policy.',
  },
  {
    title: 'Availability & Changes',
    body: 'Service may be updated, suspended, or modified for maintenance or security. We do not guarantee uninterrupted availability.',
  },
  {
    title: 'Limitation of Liability',
    body: 'AISU is provided on an “as is” basis. To the fullest extent permitted by law, AISU is not liable for indirect or consequential damages.',
  },
  {
    title: 'Governing Law & Contact',
    body: 'These terms are governed by Indian law. For questions, contact the AISU admin team.',
  },
];

function Terms() {
  return (
    <SimplePage title="Terms & Conditions" subtitle="The rules that govern use of the AISU Portal">
      <section className="dashboard-section users-section">
        <div className="recent-users-list">
          {sections.map((s) => (
            <div key={s.title} className="user-item" style={{ alignItems: 'flex-start' }}>
              <div className="user-avatar-small" aria-hidden>📜</div>
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

export default Terms;
