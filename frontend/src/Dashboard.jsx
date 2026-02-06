import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/');
    } else {
      setLoading(false);
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    navigate('/');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>AISU Portal Dashboard</h1>
        <div className="user-info">
          <span>Welcome, Admin</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome to Your Dashboard</h2>
          <p>You have successfully logged in using JWT authentication.</p>
        </div>

        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Dashboard Access</h3>
            <p>Your JWT token is valid and stored securely.</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;

