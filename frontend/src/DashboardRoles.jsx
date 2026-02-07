
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from './Navigation';
import aisuLogo from './assets/aisu-logo.jpg';
import './Dashboard.css';

/**
 * Logout handler hook
 */
function useLogout() {
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/';
  };
  return logout;
}

/**
 * DashboardLayout - Layout wrapper with Navigation sidebar
 */
function DashboardLayout({ children, user }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className={`app-layout ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      <Navigation user={user} isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      {isSidebarOpen && <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)} />}
      <main className="main-content">
        <header className="global-header">
          <div className="global-left">
            <button
              className="global-icon-button hamburger"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              aria-label="Toggle navigation"
            >
              ☰
            </button>
            <a className="global-brand" href="/dashboard">
              <img src={aisuLogo} alt="AISU logo" className="global-logo" />
              <div className="global-brand-text">
                <span className="brand-name">All India Students Union</span>
                <span className="brand-sub">Centralized Member Management</span>
              </div>
            </a>
          </div>
          <div className="global-actions">
            <div className="page-context">
              <span className="page-title">Dashboard</span>
            </div>
            <button type="button" className="global-icon-button" aria-label="Notifications">
              🔔
            </button>
            <a href="/profile" className="global-avatar" aria-label="Open profile">
              {user?.photo_url ? (
                <img src={user.photo_url} alt="Profile" />
              ) : (
                (user?.username?.[0]?.toUpperCase() || 'A')
              )}
            </a>
          </div>
        </header>
        <div className="dashboard-content with-global-header">
          {children}
        </div>
      </main>
    </div>
  );
}

/**
 * StatsCard - Reusable statistics card component
 */
function StatsCard({ title, value, icon, color, subtitle }) {
  return (
    <div className="stat-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="stat-icon" style={{ backgroundColor: color }}>
        {icon}
      </div>
      <div className="stat-content">
        <h3>{title}</h3>
        <p className="stat-number">{value}</p>
        {subtitle && <span className="stat-subtitle">{subtitle}</span>}
      </div>
    </div>
  );
}

/**
 * QuickActionCard - Quick action button card
 */
function QuickActionCard({ title, description, icon, link, color }) {
  return (
    <Link to={link} className="quick-action-card" style={{ borderTop: `3px solid ${color}` }}>
      <div className="quick-action-icon" style={{ color }}>{icon}</div>
      <h4>{title}</h4>
      <p>{description}</p>
    </Link>
  );
}

/**
 * ActivityItem - Single activity feed item
 */
function ActivityItem({ icon, title, description, time, color }) {
  return (
    <div className="activity-item">
      <div className="activity-icon" style={{ backgroundColor: color }}>
        {icon}
      </div>
      <div className="activity-content">
        <p className="activity-title">{title}</p>
        <p className="activity-description">{description}</p>
        <span className="activity-time">{time}</span>
      </div>
    </div>
  );
}

/**
 * NotificationBadge - Notification indicator
 */
function NotificationBadge({ count }) {
  if (count <= 0) return null;
  return <span className="notification-badge">{count > 9 ? '9+' : count}</span>;
}

/**
 * AdminDashboard - Component for Super Admin users
 */
export function AdminDashboard({ user }) {
  const [counts, setCounts] = useState({ total_users: 0, total_states: 0, total_districts: 0 });
  const [recentUsers, setRecentUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    server: 'unknown',
    database: 'unknown',
    email: 'unknown',
    checked_at: null,
  });
  const logout = useLogout();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');

    fetch('/accounts/dashboard-counts/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to load dashboard counts');
        return response.json();
      })
      .then(data => setCounts(data))
      .catch(console.error);

    fetch('/accounts/manage-users/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to load users');
        return response.json();
      })
      .then(data => {
        const users = (data?.users || [])
          .sort((a, b) => new Date(b.date_joined || 0) - new Date(a.date_joined || 0))
          .slice(0, 5);
        setRecentUsers(users);
        const mappedActivities = users.map(u => ({
          icon: '👤',
          title: `${u.username} joined`,
          description: `${formatRole(u.role || 'member')}${u.state ? ` • ${u.state}` : ''}`,
          time: formatRelativeTime(u.date_joined),
          color: '#4caf50',
        }));
        setActivities(mappedActivities);
      })
      .catch(err => {
        console.error(err);
        setRecentUsers([]);
        setActivities([]);
      });

    fetch('/accounts/system-status/', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load system status');
        return res.json();
      })
      .then(data => setSystemStatus(data))
      .catch(err => {
        console.error(err);
        setSystemStatus({
          server: 'error',
          database: 'error',
          email: 'error',
          checked_at: null,
        });
      });
  }, []);

  const formatRole = (role) => {
    return role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

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

  const statusLabel = (status) => {
    switch (status) {
      case 'online': return 'Online';
      case 'error': return 'Issue';
      case 'not_configured': return 'Not Configured';
      default: return 'Unknown';
    }
  };

  const statusClass = (status) => {
    switch (status) {
      case 'online': return 'online';
      case 'not_configured': return 'warning';
      case 'error': return 'error';
      default: return 'warning';
    }
  };

  return (
    <DashboardLayout user={user}>
      <div className="dashboard-container">
        <div className="dashboard-content">
          {/* Welcome Section */}
          <div className="welcome-section">
            <div className="welcome-card">
              <div className="welcome-content">
                <h2>Welcome back, {user?.first_name || user?.username || 'Member'}! 👋</h2>
                <p>Here's what's happening with your union portal today.</p>
              </div>
              <div className="welcome-actions">
                <Link to="/users" className="action-button primary">
                  <span>👥</span> Manage Members
                </Link>
                <Link to="/designations" className="action-button secondary">
                  <span>🏷️</span> Roles
                </Link>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <section className="dashboard-section">
            <h2 className="section-title">Statistics Overview</h2>
            <div className="stats-grid">
              <StatsCard 
                title="Total Members" 
                value={counts.total_users || 0} 
                icon="👥" 
                color="#4caf50"
                subtitle="Active portal members"
              />
              <StatsCard 
                title="Total States" 
                value={counts.total_states || 0} 
                icon="🗺️" 
                color="#2196f3"
                subtitle="States covered"
              />
              <StatsCard 
                title="Total Districts" 
                value={counts.total_districts || 0} 
                icon="📍" 
                color="#ff9800"
                subtitle="Districts managed"
              />
              <StatsCard 
                title="Active Today" 
                value="24" 
                icon="🟢" 
                color="#9c27b0"
                subtitle="Members online"
              />
            </div>
          </section>

          {/* Quick Actions */}
          <section className="dashboard-section">
            <h2 className="section-title">Quick Actions</h2>
            <div className="quick-actions-grid">
              <QuickActionCard 
                title="Add New Member" 
                description="Register a new member" 
                icon="➕" 
                link="/users?action=add"
                color="#4caf50"
              />
              <QuickActionCard 
                title="Manage Members" 
                description="View and edit members" 
                icon="👥" 
                link="/users"
                color="#2196f3"
              />
              <QuickActionCard 
                title="Roles & Permissions" 
                description="Manage role designations" 
                icon="🏷️" 
                link="/designations"
                color="#ff9800"
              />
              <QuickActionCard 
                title="My Profile" 
                description="Edit your profile" 
                icon="👤" 
                link="/profile"
                color="#9c27b0"
              />
            </div>
          </section>

          {/* Two Column Layout for Activities and Recent Users */}
          <div className="dashboard-columns">
            {/* Recent Activity */}
            <section className="dashboard-section activity-section">
              <div className="section-header">
                <h2 className="section-title">Recent Activity</h2>
                <Link to="/activity" className="view-all-link">View All →</Link>
              </div>
              <div className="activity-feed">
                {activities.map((activity, index) => (
                  <ActivityItem key={index} {...activity} />
                ))}
              </div>
            </section>

            {/* Recent Users */}
            <section className="dashboard-section users-section">
              <div className="section-header">
                <h2 className="section-title">Recent Members</h2>
                <Link to="/users" className="view-all-link">View All →</Link>
              </div>
              <div className="recent-users-list">
                {recentUsers.map(user => (
                  <div key={user.id} className="user-item">
                    <div className="user-avatar-small">
                      {user.username[0].toUpperCase()}
                    </div>
                    <div className="user-details">
                      <span className="user-username">{user.username}</span>
                      <span className="user-meta">{formatRole(user.role)} • {user.state}</span>
                    </div>
                    <button className="user-action-btn">→</button>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* System Health */}
          <section className="dashboard-section">
            <h2 className="section-title">Portal Status</h2>
            <div className="system-health-grid">
              <div className="health-card">
                <div className="health-icon">🖥️</div>
                <div className="health-info">
                  <h4>Server Status</h4>
                  <span className={`health-status ${statusClass(systemStatus.server)}`}>
                    ● {statusLabel(systemStatus.server)}
                  </span>
                </div>
                <div className="health-value">{systemStatus.server === 'online' ? 'OK' : 'Check'}</div>
              </div>
              <div className="health-card">
                <div className="health-icon">💾</div>
                <div className="health-info">
                  <h4>Database</h4>
                  <span className={`health-status ${statusClass(systemStatus.database)}`}>
                    ● {statusLabel(systemStatus.database)}
                  </span>
                </div>
                <div className="health-value">{systemStatus.database === 'online' ? 'Connected' : 'Check'}</div>
              </div>
              <div className="health-card">
                <div className="health-icon">📧</div>
                <div className="health-info">
                  <h4>Email Service</h4>
                  <span className={`health-status ${statusClass(systemStatus.email)}`}>
                    ● {statusLabel(systemStatus.email)}
                  </span>
                </div>
                <div className="health-value">
                  {systemStatus.email === 'online'
                    ? 'Active'
                    : systemStatus.email === 'not_configured'
                      ? 'Configure'
                      : 'Issue'}
                </div>
              </div>
              <div className="health-card">
                <div className="health-icon">⏱️</div>
                <div className="health-info">
                  <h4>Last Check</h4>
                  <span className="health-status online">
                    {systemStatus.checked_at ? new Date(systemStatus.checked_at).toLocaleTimeString() : '—'}
                  </span>
                </div>
                <div className="health-value">Live</div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}

/**
 * ITTeamDashboard - Component for IT Team users
 */
export function ITTeamDashboard({ user }) {
  const [systemStats, setSystemStats] = useState({
    uptime: '15 days',
    activeTickets: 12,
    serverLoad: '32%',
    diskUsage: '45%'
  });
  const logout = useLogout();

  return (
    <DashboardLayout user={user}>
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="welcome-section">
            <div className="welcome-card it-theme">
              <div className="welcome-content">
                <h2>IT Support Portal 🛠️</h2>
                <p>Monitor system health and manage technical operations.</p>
              </div>
              <div className="welcome-actions">
                <Link to="/designations" className="action-button primary">
                  <span>🏷️</span> Roles
                </Link>
                <Link to="/profile" className="action-button secondary">
                  <span>👤</span> My Profile
                </Link>
              </div>
            </div>
          </div>

          <section className="dashboard-section">
            <h2 className="section-title">System Overview</h2>
            <div className="stats-grid">
              <StatsCard 
                title="System Uptime" 
                value={systemStats.uptime} 
                icon="⏱️" 
                color="#4caf50"
                subtitle="Since last restart"
              />
              <StatsCard 
                title="Active Tickets" 
                value={systemStats.activeTickets} 
                icon="🎫" 
                color="#ff9800"
                subtitle="Pending support"
              />
              <StatsCard 
                title="Server Load" 
                value={systemStats.serverLoad} 
                icon="📊" 
                color="#2196f3"
                subtitle="Current usage"
              />
              <StatsCard 
                title="Disk Usage" 
                value={systemStats.diskUsage} 
                icon="💾" 
                color="#f44336"
                subtitle="Storage used"
              />
            </div>
          </section>

          <section className="dashboard-section">
            <h2 className="section-title">Quick Actions</h2>
            <div className="quick-actions-grid">
              <QuickActionCard 
                title="Support Tickets" 
                description="View and manage tickets" 
                icon="🎫" 
                link="/tickets"
                color="#ff9800"
              />
              <QuickActionCard 
                title="System Logs" 
                description="View system logs" 
                icon="📋" 
                link="/logs"
                color="#2196f3"
              />
              <QuickActionCard 
                title="Member Management" 
                description="Manage member accounts" 
                icon="👥" 
                link="/users"
                color="#4caf50"
              />
              <QuickActionCard 
                title="Profile Settings" 
                description="Update your profile" 
                icon="⚙️" 
                link="/profile"
                color="#9c27b0"
              />
            </div>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}

/**
 * StateTeamDashboard - Component for State Team users
 */
export function StateTeamDashboard({ user }) {
  const [counts, setCounts] = useState({ total_users: 0, total_states: 0, total_districts: 0 });
  const logout = useLogout();

  useEffect(() => {
    fetch('/accounts/dashboard-counts/')
      .then(response => response.json())
      .then(data => setCounts(data))
      .catch(console.error);
  }, []);

  return (
    <DashboardLayout user={user}>
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="welcome-section">
            <div className="welcome-card state-theme">
              <div className="welcome-content">
                <h2>State Portal 🏛️</h2>
                <p>Manage state-level operations for {user?.state || 'your state'}.</p>
              </div>
              <div className="welcome-actions">
                <Link to="/designations" className="action-button primary">
                  <span>🏷️</span> Roles
                </Link>
                <Link to="/profile" className="action-button secondary">
                  <span>👤</span> My Profile
                </Link>
              </div>
            </div>
          </div>

          <section className="dashboard-section">
            <h2 className="section-title">State Statistics</h2>
            <div className="stats-grid">
              <StatsCard 
                title="Total Members" 
                value={counts.total_users || 0} 
                icon="👥" 
                color="#4caf50"
                subtitle="In your state"
              />
              <StatsCard 
                title="Districts" 
                value={counts.total_districts || 0} 
                icon="📍" 
                color="#ff9800"
                subtitle="Under your state"
              />
              <StatsCard 
                title="Active Members" 
                value="18" 
                icon="🟢" 
                color="#2196f3"
                subtitle="Currently active"
              />
              <StatsCard 
                title="Pending Tasks" 
                value="5" 
                icon="📋" 
                color="#9c27b0"
                subtitle="Awaiting action"
              />
            </div>
          </section>

          <section className="dashboard-section">
            <h2 className="section-title">Quick Actions</h2>
            <div className="quick-actions-grid">
              <QuickActionCard 
                title="View Districts" 
                description="Browse all districts" 
                icon="🗺️" 
                link="/districts"
                color="#4caf50"
              />
              <QuickActionCard 
                title="Manage Members" 
                description="State member management" 
                icon="👥" 
                link="/users"
                color="#2196f3"
              />
              <QuickActionCard 
                title="Roles" 
                description="Role designations" 
                icon="🏷️" 
                link="/designations"
                color="#ff9800"
              />
              <QuickActionCard 
                title="Profile" 
                description="Update your profile" 
                icon="👤" 
                link="/profile"
                color="#9c27b0"
              />
            </div>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}

/**
 * DistrictTeamDashboard - Component for District Team users
 */
export function DistrictTeamDashboard({ user }) {
  const logout = useLogout();

  return (
    <DashboardLayout user={user}>
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="welcome-section">
            <div className="welcome-card district-theme">
              <div className="welcome-content">
                <h2>District Portal 🏘️</h2>
                <p>Manage operations for {user?.district || 'your district'}.</p>
              </div>
              <div className="welcome-actions">
                <Link to="/profile" className="action-button primary">
                  <span>👤</span> My Profile
                </Link>
              </div>
            </div>
          </div>

          <section className="dashboard-section">
            <h2 className="section-title">Quick Overview</h2>
            <div className="stats-grid">
              <StatsCard 
                title="Profile Status" 
                value="Active" 
                icon="✅" 
                color="#4caf50"
                subtitle="Your account"
              />
              <StatsCard 
                title="District" 
                value={user?.district || 'N/A'} 
                icon="📍" 
                color="#2196f3"
                subtitle="Your district"
              />
              <StatsCard 
                title="Role" 
                value="District Team" 
                icon="👤" 
                color="#ff9800"
                subtitle="Current role"
              />
              <StatsCard 
                title="Last Login" 
                value="Today" 
                icon="🕐" 
                color="#9c27b0"
                subtitle="Session time"
              />
            </div>
          </section>

          <section className="dashboard-section">
            <h2 className="section-title">Quick Actions</h2>
            <div className="quick-actions-grid">
              <QuickActionCard 
                title="My Profile" 
                description="View and edit profile" 
                icon="👤" 
                link="/profile"
                color="#4caf50"
              />
              <QuickActionCard 
                title="Settings" 
                description="Account settings" 
                icon="⚙️" 
                link="/settings"
                color="#2196f3"
              />
              <QuickActionCard 
                title="Help" 
                description="Get support" 
                icon="❓" 
                link="/help"
                color="#ff9800"
              />
              <QuickActionCard 
                title="Contact" 
                description="Contact support" 
                icon="✉️" 
                link="/contact"
                color="#9c27b0"
              />
            </div>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}
