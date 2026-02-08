import React, { useState, useEffect } from 'react';
import Navigation from './Navigation';
import './Dashboard.css';
import aisuLogo from './assets/aisu-logo.jpg';
import notificationService from './services/notificationService';

function SimplePage({ title, subtitle, children }) {
  const user = React.useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || {};
    } catch (e) {
      return {};
    }
  }, []);

  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Load notifications when component mounts
  useEffect(() => {
    loadNotifications();
    
    // Set up polling to refresh notifications periodically
    const interval = setInterval(loadNotifications, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      // Refresh notifications after marking one as read
      loadNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      // Refresh notifications after marking all as read
      loadNotifications();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

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
            <div className="notification-container">
              <button 
                type="button" 
                className="global-icon-button" 
                aria-label="Notifications"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                🔔
                {unreadCount > 0 && (
                  <span className="notification-badge">{unreadCount}</span>
                )}
              </button>
              
              {showNotifications && (
                <div className="header-notifications-dropdown">
                  <div className="notifications-header">
                    <h4>Notifications</h4>
                    <button onClick={() => setShowNotifications(false)}>×</button>
                  </div>
                  <div className="notifications-list">
                    {isLoading ? (
                      <div className="notification-item">
                        <p>Loading notifications...</p>
                      </div>
                    ) : notifications.length === 0 ? (
                      <div className="notification-item">
                        <p>No notifications</p>
                      </div>
                    ) : (
                      notifications.map(notification => (
                        <div 
                          key={notification.id} 
                          className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                          onClick={() => handleMarkAsRead(notification.id)}
                        >
                          <p><strong>{notification.title}</strong><br/>{notification.message}</p>
                          <span className="notification-time">
                            {new Date(notification.created_at).toLocaleString()}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                  {notifications.length > 0 && (
                    <div className="notifications-footer">
                      <button onClick={handleMarkAllAsRead} className="mark-all-read-button">
                        Mark all as read
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
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
      
      <style jsx>{`
        .notification-container {
          position: relative;
          display: inline-block;
        }
        
        .notification-badge {
          position: absolute;
          top: -5px;
          right: -5px;
          background: #ef4444;
          color: white;
          font-size: 10px;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 10px;
          min-width: 18px;
          text-align: center;
        }
        
        .header-notifications-dropdown {
          position: absolute;
          right: 0;
          top: 100%;
          background: white;
          border-radius: 8px;
          box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
          z-index: 1001;
          margin-top: 8px;
          width: 300px;
          overflow: hidden;
        }
        
        .notifications-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-bottom: 1px solid var(--slate-100);
          background: var(--slate-50);
        }
        
        .notifications-header h4 {
          font-size: 14px;
          font-weight: 600;
          color: var(--slate-800);
          margin: 0;
        }
        
        .notifications-header button {
          background: none;
          border: none;
          font-size: 20px;
          color: var(--slate-600);
          cursor: pointer;
          padding: 0;
          line-height: 1;
        }
        
        .notifications-list {
          max-height: 300px;
          overflow-y: auto;
        }
        
        .notification-item {
          padding: 12px 16px;
          border-bottom: 1px solid var(--slate-100);
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .notification-item:last-child {
          border-bottom: none;
        }
        
        .notification-item:hover {
          background: var(--slate-50);
        }
        
        .notification-item.unread {
          background: #e0ecff;
        }
        
        .notification-item p {
          font-size: 13px;
          color: var(--slate-800);
          margin: 0 0 4px 0;
        }
        
        .notification-time {
          font-size: 11px;
          color: var(--slate-400);
        }
        
        .notifications-footer {
          padding: 12px 16px;
          border-top: 1px solid var(--slate-100);
          background: var(--slate-50);
        }
        
        .mark-all-read-button {
          background: none;
          border: none;
          color: var(--blue-600);
          cursor: pointer;
          font-size: 12px;
          text-decoration: underline;
          padding: 0;
          margin: 0;
        }
        
        .mark-all-read-button:hover {
          color: var(--blue-800);
        }
      `}</style>
    </div>
  );
}

export default SimplePage;
