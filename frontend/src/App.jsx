import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import RoleBasedDashboard from './RoleBasedDashboard';
import DesignationsList from './DesignationsList';
import PrivateRoute from './PrivateRoute';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <RoleBasedDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/designations"
        element={
          <PrivateRoute>
            <DesignationsList />
          </PrivateRoute>
        }
      />
      {/* Catch all route - redirect to login */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
