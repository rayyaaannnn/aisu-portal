import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminDashboard, ITTeamDashboard, StateTeamDashboard, DistrictTeamDashboard } from './DashboardRoles';
import AccessDenied from './AccessDenied';

/**
 * RoleBasedDashboard - Renders different dashboards based on user.role
 * 
 * Routes to appropriate dashboard component based on user role:
 * - "super_admin" → AdminDashboard
 * - "it_team" → ITTeamDashboard
 * - "state_team" → StateTeamDashboard
 * - "district_team" → DistrictTeamDashboard
 * - Otherwise → AccessDenied
 */
function RoleBasedDashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user info from JWT token or localStorage
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/');
      return;
    }

    // Get user from localStorage (set during login)
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Fetch user info from API
      fetch('/accounts/user-info/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
        .then(response => response.json())
        .then(data => {
          setUser(data);
          localStorage.setItem('user', JSON.stringify(data));
        })
        .catch(() => {
          setUser({ username: 'User', role: 'district_team' });
        });
    }
    setLoading(false);
  }, [navigate]);

  // Show loading state
  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  // Determine which dashboard to show based on user role
  const renderDashboard = () => {
    const userRole = user?.role?.toLowerCase();

    switch (userRole) {
      case 'super_admin':
        return <AdminDashboard user={user} />;
      case 'it_team':
        return <ITTeamDashboard user={user} />;
      case 'state_team':
        return <StateTeamDashboard user={user} />;
      case 'district_team':
        return <DistrictTeamDashboard user={user} />;
      default:
        return <AccessDenied />;
    }
  };

  return renderDashboard();
}

export default RoleBasedDashboard;

