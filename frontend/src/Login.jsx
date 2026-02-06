import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);

        const userInfoResponse = await fetch('/accounts/user-info/', {
          headers: { Authorization: `Bearer ${data.access}` },
        });

        let redirectPath = '/dashboard';
        if (userInfoResponse.ok) {
          const userData = await userInfoResponse.json();
          localStorage.setItem('user', JSON.stringify(userData));

          switch (userData.role) {
            case 'super_admin':
            case 'it_team':
            case 'state_team':
            case 'district_team':
              redirectPath = '/dashboard';
              break;
            default:
              redirectPath = '/dashboard';
          }
        }

        navigate(redirectPath);
      } else {
        if (data.detail) {
          setError(data.detail);
        } else if (data.non_field_errors) {
          setError(data.non_field_errors[0]);
        } else {
          setError('Invalid username or password. Please try again.');
        }
      }
    } catch (err) {
      setError('Unable to connect to server. Please check your connection.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="bg-shape shape-1"></div>
        <div className="bg-shape shape-2"></div>
        <div className="bg-shape shape-3"></div>
      </div>

      <div className="login-card">
        <div className="login-brand">
          <div className="brand-logo">
            <span className="logo-icon">🎓</span>
          </div>
          <h1 className="brand-title">All India Students Union</h1>
        </div>

        <div className="login-body">
          <div className="login-header-section">
            <h2>Welcome to AISU Sign in Page</h2>
            <p>Sign in to access your dashboard</p>
          </div>

          {error && (
            <div className="error-alert">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div className={`form-group ${focusedField === 'username' ? 'focused' : ''}`}>
              <label htmlFor="username">
                <span className="label-icon">👤</span>
                Username
              </label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onFocus={() => setFocusedField('username')}
                  onBlur={() => setFocusedField(null)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter your username"
                  required
                  autoComplete="username"
                  disabled={loading}
                />
              </div>
            </div>

            <div className={`form-group ${focusedField === 'password' ? 'focused' : ''}`}>
              <label htmlFor="password">
                <span className="label-icon">🔒</span>
                Password
              </label>
              <div className="input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter your password"
                  required
                  autoComplete="current-password"
                  disabled={loading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            <div className="form-options">
              <label className="remember-me">
                <input type="checkbox" />
                <span className="checkmark"></span>
                Remember me
              </label>
              <a href="#forgot" className="forgot-password">Forgot password?</a>
            </div>

            <button
              type="submit"
              className={`login-button ${loading ? 'loading' : ''}`}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <span className="btn-arrow">→</span>
                </>
              )}
            </button>
          </form>

          <div className="login-footer">
            <p>Secured with JWT Authentication</p>
          </div>

          <div className="login-info">
            <div className="info-badge">
              <span className="badge-icon">🔐</span>
              <span>RBAC Portal</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;