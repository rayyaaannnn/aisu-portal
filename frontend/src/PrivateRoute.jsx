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
function PrivateRoute({ children }) {
  const location = useLocation();
  
  // Check for authentication token
  const isAuthenticated = !!localStorage.getItem('accessToken');

  if (!isAuthenticated) {
    // Redirect to login while saving the current location
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  // User is authenticated, render the child component
  return children;
}

export default PrivateRoute;

