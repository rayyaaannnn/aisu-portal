import React, { useState, useEffect } from 'react';

/**
 * Logout handler
 */
function useLogout() {
  const navigate = window.location?.useNavigate?.() || (() => {});
  
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/';
  };
  
  return logout;
}

/**
 * AdminDashboard - Component for Super Admin users
 */
export function AdminDashboard({ user }) {
  const [counts, setCounts] = useState({ total_users: 0, total_states: 0, total_districts: 0 });
  const logout = useLogout();

  useEffect(() => {
    fetch('/accounts/dashboard-counts/')
      .then(response => response.json())
      .then(data => setCounts(data))
      .catch(console.error);
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.username || 'Admin'}</span>
          <button onClick={logout} className="logout-button">Logout</button>
        </div>
      </header>
      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Super Admin Panel</h2>
          <p>Manage all users and system settings.</p>
        </div>
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Users</h3>
            <p className="stat-number">{counts.total_users}</p>
          </div>
          <div className="stat-card">
            <h3>Total States</h3>
            <p className="stat-number">{counts.total_states}</p>
          </div>
          <div className="stat-card">
            <h3>Total Districts</h3>
            <p className="stat-number">{counts.total_districts}</p>
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * ITTeamDashboard - Component for IT Team users
 */
export function ITTeamDashboard({ user }) {
  const logout = useLogout();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>IT Team Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.username || 'IT Team'}</span>
          <button onClick={logout} className="logout-button">Logout</button>
        </div>
      </header>
      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>IT Support Portal</h2>
          <p>System maintenance and technical support.</p>
        </div>
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>System Status</h3>
            <p>All systems operational</p>
          </div>
          <div className="stat-card">
            <h3>Active Tickets</h3>
            <p>View and manage support tickets</p>
          </div>
        </div>
      </main>
    </div>
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
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>State Team Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.username || 'State Team'}</span>
          <button onClick={logout} className="logout-button">Logout</button>
        </div>
      </header>
      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>State Portal</h2>
          <p>Manage state-level operations. State: {user?.state || 'N/A'}</p>
        </div>
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Users</h3>
            <p className="stat-number">{counts.total_users}</p>
          </div>
          <div className="stat-card">
            <h3>Districts</h3>
            <p className="stat-number">{counts.total_districts}</p>
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * DistrictTeamDashboard - Component for District Team users
 */
export function DistrictTeamDashboard({ user }) {
  const logout = useLogout();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>District Team Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user?.username || 'District Team'}</span>
          <button onClick={logout} className="logout-button">Logout</button>
        </div>
      </header>
      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>District Portal</h2>
          <p>Manage district-level operations. District: {user?.district || 'N/A'}</p>
        </div>
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Your Profile</h3>
            <p>View and update your profile</p>
          </div>
        </div>
      </main>
    </div>
  );
}

