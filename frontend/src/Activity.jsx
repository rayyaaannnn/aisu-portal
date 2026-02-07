import React from 'react';
import SimplePage from './SimplePage';

function Activity() {
  const [feed, setFeed] = React.useState([]);

  React.useEffect(() => {
    const token = localStorage.getItem('accessToken');
    fetch('/accounts/manage-users/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load activity');
        return res.json();
      })
      .then(data => {
        const users = (data?.users || [])
          .sort((a, b) => new Date(b.date_joined || 0) - new Date(a.date_joined || 0))
          .slice(0, 20);
        const mapped = users.map(u => ({
          title: `${u.username} joined`,
          desc: `${formatRole(u.role || 'member')}${u.state ? ` • ${u.state}` : ''}`,
          time: formatRelativeTime(u.date_joined),
          icon: '👤',
          color: '#10b981',
        }));
        setFeed(mapped);
      })
      .catch(err => {
        console.error(err);
        setFeed([]);
      });
  }, []);

  const formatRole = (role) => role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());

  const formatRelativeTime = (isoString) => {
    if (!isoString) return 'Just now';
    const date = new Date(isoString);
    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <SimplePage title="Activity" subtitle="Recent changes across AISU">
      <section className="dashboard-section activity-section">
        {feed.length === 0 ? (
          <div className="activity-feed" style={{ color: 'var(--text-muted)' }}>
            No recent activity available.
          </div>
        ) : (
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
        )}
      </section>
    </SimplePage>
  );
}

export default Activity;
