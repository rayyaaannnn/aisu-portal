import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './ForgotPassword.css';
import aisuLogo from './assets/aisu-logo.jpg';

function ForgotPassword() {
  const [identifier, setIdentifier] = useState('');
  const [stage, setStage] = useState('request'); // request | confirm
  const [uid, setUid] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // On mount, detect uid/token in query params (from email link)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const uidParam = params.get('uid');
    const tokenParam = params.get('token');
    if (uidParam && tokenParam) {
      setUid(uidParam);
      setToken(tokenParam);
      setStage('confirm');
    }
  }, [location.search]);

  const handleRequest = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/accounts/password-reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier }),
      });

      if (response.ok) {
        setMessage('If an account exists, a reset link has been sent to the registered email.');
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || 'Unable to process request right now. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);

    if (!uid || !token) {
      setError('Reset link is invalid or expired. Request a new link.');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/accounts/password-reset/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          uid: uid.trim(),
          token: token.trim(),
          new_password: newPassword,
        }),
      });

      if (response.ok) {
        setMessage('Password reset successful. You can now sign in.');
        setTimeout(() => navigate('/'), 1200);
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || data.error || 'Invalid or expired token. Please retry.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => navigate('/');

  return (
    <div className="fp-page">
      <div className="fp-card">
        <div className="fp-header">
          <div className="fp-logo" aria-hidden="true">
            <img src={aisuLogo} alt="AISU logo" />
          </div>
          <div className="fp-title">
            <h1>Reset your password</h1>
            <p>Enter your username or email and we'll send a reset link.</p>
          </div>
        </div>

        {message && <div className="fp-alert success">{message}</div>}
        {error && <div className="fp-alert error">{error}</div>}

        {stage === 'request' && (
          <form className="fp-form" onSubmit={handleRequest}>
            <label className="fp-label" htmlFor="identifier">Username or email</label>
            <div className="fp-input-wrap">
              <input
                id="identifier"
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. johndoe or john@domain.com"
                required
                disabled={loading}
              />
            </div>

            <button type="submit" className={`fp-button ${loading ? 'loading' : ''}`} disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </button>
          </form>
        )}

        {stage === 'confirm' && (
          <form className="fp-form" onSubmit={handleConfirm}>
            <label className="fp-label" htmlFor="newPassword">New password</label>
            <div className="fp-input-wrap">
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                required
                disabled={loading}
              />
            </div>

            <label className="fp-label" htmlFor="confirmPassword">Confirm new password</label>
            <div className="fp-input-wrap">
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter new password"
                required
                disabled={loading}
              />
            </div>

            <button type="submit" className={`fp-button ${loading ? 'loading' : ''}`} disabled={loading}>
              {loading ? 'Resetting...' : 'Reset password'}
            </button>

            <button type="button" className="fp-link subtle" onClick={() => setStage('request')} disabled={loading}>
              ← Start over
            </button>
          </form>
        )}

        <div className="fp-footer">
          <button type="button" className="fp-link" onClick={goBack}>← Back to sign in</button>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
