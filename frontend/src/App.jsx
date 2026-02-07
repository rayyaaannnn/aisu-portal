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
        path="/users"
        element={
          <PrivateRoute>
            <UserManagement />
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
          <PrivateRoute>
            <Tickets />
          </PrivateRoute>
        }
      />
      <Route
        path="/logs"
        element={
          <PrivateRoute>
            <Logs />
          </PrivateRoute>
        }
      />
      <Route
        path="/activity"
        element={
          <PrivateRoute>
            <Activity />
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute>
            <Settings />
          </PrivateRoute>
        }
      />
      <Route
        path="/help"
        element={
          <PrivateRoute>
            <Help />
          </PrivateRoute>
        }
      />
      <Route
        path="/contact"
        element={
          <PrivateRoute>
            <Contact />
          </PrivateRoute>
        }
      />
      <Route
        path="/districts"
        element={
          <PrivateRoute>
            <Districts />
          </PrivateRoute>
        }
      />
      {/* Catch all route - redirect to login */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
