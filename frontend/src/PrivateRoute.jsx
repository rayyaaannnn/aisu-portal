import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * PrivateRoute component that protects routes requiring authentication.
 * 
 * Usage:
 * <PrivateRoute>
 *   <Dashboard />
 * </PrivateRoute>
 * 
 * Or with props:
 * <PrivateRoute>
 *   <ProtectedComponent prop="value" />
 * </PrivateRoute>
 */
function PrivateRoute({ children, allowedRoles }) {
  const location = useLocation();
  
  // Check for authentication token
  const isAuthenticated = !!localStorage.getItem('accessToken');
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || {};
    } catch (e) {
      return {};
    }
  })();

  if (!isAuthenticated) {
    // Redirect to login while saving the current location
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role = user?.role;
    const isAllowed = allowedRoles.includes(role);
    if (!isAllowed) {
      return <Navigate to="/access-denied" replace />;
    }
  }

  // User is authenticated, render the child component
  return children;
}

export default PrivateRoute;
