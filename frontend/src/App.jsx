import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login.jsx';
import RoleBasedDashboard from './RoleBasedDashboard';
import DesignationsList from './DesignationsList';
import UserManagement from './UserManagement';
import Profile from './Profile';
import PrivateRoute from './PrivateRoute';
import ForgotPassword from './ForgotPassword';
import Tickets from './Tickets';
import Logs from './Logs';
import Activity from './Activity';
import Settings from './Settings';
import Help from './Help';
import Contact from './Contact';
import Districts from './Districts';
import Terms from './Terms';
import Privacy from './Privacy';
import AccessDenied from './AccessDenied';
import LoginLogs from './LoginLogs';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team', 'district_team']}>
            <RoleBasedDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/users"
        element={
          <PrivateRoute allowedRoles={['super_admin']}>
            <UserManagement />
          </PrivateRoute>
        }
      />
      <Route
        path="/designations"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team', 'district_team']}>
            <DesignationsList />
          </PrivateRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <PrivateRoute>
            <Profile />
          </PrivateRoute>
        }
      />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route
        path="/tickets"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team']}>
            <Tickets />
          </PrivateRoute>
        }
      />
      <Route
        path="/login-logs"
        element={
          <PrivateRoute allowedRoles={['super_admin']}>
            <LoginLogs />
          </PrivateRoute>
        }
      />
      <Route
        path="/logs"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team']}>
            <Logs />
          </PrivateRoute>
        }
      />
      <Route
        path="/activity"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team', 'district_team']}>
            <Activity />
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team']}>
            <Settings />
          </PrivateRoute>
        }
      />
      <Route
        path="/help"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team', 'district_team']}>
            <Help />
          </PrivateRoute>
        }
      />
      <Route
        path="/contact"
        element={
          <PrivateRoute allowedRoles={['super_admin', 'it_team', 'state_team', 'district_team']}>
            <Contact />
          </PrivateRoute>
        }
      />
      <Route
        path="/districts"
        element={
          <PrivateRoute allowedRoles={['state_team', 'district_team', 'super_admin']}>
            <Districts />
          </PrivateRoute>
        }
      />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/access-denied" element={<AccessDenied />} />
      {/* Catch all route - redirect to login */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
