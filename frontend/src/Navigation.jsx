
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation({ user }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const getMenuItems = () => {
    const role = user?.role?.toLowerCase();
    const baseItems = [
      { path: '/dashboard', label: 'Dashboard', icon: '📊' }
    ];

    switch (role) {
      case 'super_admin':
        return [
          ...baseItems,
          { path: '/users', label: 'User Management', icon: '👥' },
          { path: '/designations', label: 'Designations', icon: '🏷️' },
        ];
      case 'it_team':
        return [...baseItems, { path: '/designations', label: 'Designations', icon: '🏷️' }];
      case 'state_team':
        return [...baseItems, { path: '/designations', label: 'Designations', icon: '🏷️' }];
      default:
        return baseItems;
    }
  };

  const getNotifications = () => {
    return [
      { id: 1, message: 'New update available', time: '2 hours ago', read: false },
      { id: 2, message: 'Your profile was updated', time: '5 hours ago', read: false },
      { id: 3, message: 'Welcome to AISU!', time: '1 day ago', read: true },
    ];
  };

  const menuItems = getMenuItems();
  const notifications = getNotifications();
  const unreadCount = notifications.filter(n => !n.read).length;
  const userRole = user?.role?.replace('_', ' ').toUpperCase() || 'USER';

  return (
    <nav className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-text">🎓 AISU</span>
        </div>
        <button onClick={() => setIsCollapsed(!isCollapsed)} className="collapse-button">
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      <div className="sidebar-content">
        <div className="user-info">
          <div className="user-avatar">
            {user?.first_name?.[0] || user?.username?.[0] || 'U'}
          </div>
          {!isCollapsed && (
            <div className="user-details">
              <div className="user-name">{user?.first_name} {user?.last_name}</div>
              <div className="user-role">{userRole}</div>
            </div>
          )}
        </div>

        <ul className="nav-menu">
          {menuItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link to={item.path} className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}>
                <span className="nav-icon">{item.icon}</span>
                {!isCollapsed && <span className="nav-label">{item.label}</span>}
              </Link>
            </li>
          ))}
          <li className="nav-item">
            <Link to="/profile" className={`nav-link ${location.pathname === '/profile' ? 'active' : ''}`}>
              <span className="nav-icon">👤</span>
              {!isCollapsed && <span className="nav-label">Profile</span>}
            </Link>
          </li>
        </ul>

        {!isCollapsed && (
          <div className="sidebar-notifications">
            <button 
              className="notification-button"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <span className="nav-icon">🔔</span>
              <span className="nav-label">Notifications</span>
              {unreadCount > 0 && (
                <span className="notification-count">{unreadCount}</span>
              )}
            </button>
            
            {showNotifications && (
              <div className="notifications-dropdown">
                <div className="notifications-header">
                  <h4>Notifications</h4>
                  <button onClick={() => setShowNotifications(false)}>×</button>
                </div>
                <div className="notifications-list">
                  {notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${!notification.read ? 'unread' : ''}`}>
                      <p>{notification.message}</p>
                      <span className="notification-time">{notification.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-button">
          <span className="nav-icon">🚪</span>
          {!isCollapsed && <span className="nav-label">Logout</span>}
        </button>
      </div>

      {/* Inline styles for notification features */}
      <style>{`
        .sidebar-notifications {
          position: relative;
          padding: 0 12px;
          margin-top: 8px;
        }

        .notification-button {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: rgba(255, 255, 255, 0.05);
          border: none;
          border-radius: 8px;
          color: rgba(255, 255, 255, 0.85);
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
        }

        .notification-button:hover {
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }

        .notification-count {
          position: absolute;
          right: 12px;
          background: #f44336;
          color: white;
          font-size: 10px;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 10px;
          min-width: 18px;
          text-align: center;
        }

        .notifications-dropdown {
          position: absolute;
          left: 0;
          right: 0;
          top: 100%;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          z-index: 1001;
          margin-top: 8px;
          overflow: hidden;
        }

        .notifications-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-bottom: 1px solid #e0e0e0;
          background: #f8f9fa;
        }

        .notifications-header h4 {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          margin: 0;
        }

        .notifications-header button {
          background: none;
          border: none;
          font-size: 20px;
          color: #666;
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
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .notification-item:last-child {
          border-bottom: none;
        }

        .notification-item:hover {
          background: #f8f9fa;
        }

        .notification-item.unread {
          background: #e3f2fd;
        }

        .notification-item p {
          font-size: 13px;
          color: #333;
          margin: 0 0 4px 0;
        }

        .notification-time {
          font-size: 11px;
          color: #999;
        }

        .sidebar.collapsed .sidebar-notifications {
          padding: 0;
        }

        .sidebar.collapsed .notification-button {
          justify-content: center;
          padding: 12px;
        }

        .sidebar.collapsed .notifications-dropdown {
          left: 100%;
          top: 0;
          margin-left: 8px;
          width: 250px;
        }
      `}</style>
    </nav>
  );
}

export default Navigation;

