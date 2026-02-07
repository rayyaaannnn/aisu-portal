import React from 'react';
import Navigation from './Navigation';
import './Dashboard.css';
import aisuLogo from './assets/aisu-logo.jpg';

function SimplePage({ title, subtitle, children }) {
  const user = React.useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || {};
    } catch (e) {
      return {};
    }
  }, []);

  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);

  return (
    <div className={`app-layout ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
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
              <span className="page-title">{title}</span>
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
        <div className="dashboard-content">
          <div className="page-header" style={{ marginBottom: '12px' }}>
            <h1>{title}</h1>
            {subtitle && <p className="header-subtitle">{subtitle}</p>}
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}

export default SimplePage;
