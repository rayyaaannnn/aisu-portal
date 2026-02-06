import React from 'react';
import { Link } from 'react-router-dom';
import './AccessDenied.css';

/**
 * AccessDenied - Simple component that displays an access denied message
 * with a link to go back to the homepage.
 */
function AccessDenied() {
  return (
    <div className="access-denied-container">
      <div className="access-denied-card">
        <div className="access-denied-icon">🚫</div>
        <h1>Access Denied</h1>
        <p>You do not have permission to access this page.</p>
        <p className="access-denied-hint">
          Please contact the administrator if you believe this is an error.
        </p>
        <Link to="/" className="access-denied-link">
          Go Back to Homepage
        </Link>
      </div>
    </div>
  );
}

export default AccessDenied;

