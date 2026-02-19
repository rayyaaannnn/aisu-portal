import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';
import aisuLogo from './assets/aisu-logo.jpg';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState(null);
  const [theme, setTheme] = useState('light');
  const [lastLoginAt, setLastLoginAt] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  useEffect(() => {
    const storedTheme = localStorage.getItem('aisuTheme');
    const nextTheme = storedTheme === 'dark' ? 'dark' : 'light';
    setTheme(nextTheme);
    document.body.classList.toggle('theme-dark', nextTheme === 'dark');
  }, []);

  useEffect(() => {
    const storedLastLogin = localStorage.getItem('lastLoginAt');
    if (storedLastLogin) {
      setLastLoginAt(storedLastLogin);
    }
  }, []);

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
        localStorage.setItem('lastLoginAt', new Date().toISOString());

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

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('aisuTheme', nextTheme);
    document.body.classList.toggle('theme-dark', nextTheme === 'dark');
  };

  const lastLoginText = lastLoginAt
    ? new Date(lastLoginAt).toLocaleString()
    : 'Not available yet';

  const handleRipple = (e) => {
    const button = e.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    const rect = button.getBoundingClientRect();

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - rect.left - radius}px`;
    circle.style.top = `${e.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');

    const existing = button.getElementsByClassName('ripple')[0];
    if (existing) {
      existing.remove();
    }
    button.appendChild(circle);
  };

  return (
    <div className="login-page">
      <div className="login-layout">
        <aside className="branding-panel" aria-hidden="true">
          <div className="branding-inner">
            <div className="brand-mark">
              <div className="brand-emblem">
                <img src={aisuLogo} alt="AISU logo" />
              </div>
              <div className="brand-text">
                <h1>All India Students Union</h1>
                <p>Centralized Member Management Portal</p>
              </div>
            </div>

            <div className="brand-illustration">
              <svg viewBox="0 0 420 260" role="img" aria-label="Connected student network illustration">
                <defs>
                  <linearGradient id="orb" x1="0" x2="1" y1="0" y2="1">
                    <stop offset="0" stopColor="#8ec5ff" stopOpacity="0.9" />
                    <stop offset="1" stopColor="#b992ff" stopOpacity="0.4" />
                  </linearGradient>
                </defs>
                <circle cx="90" cy="90" r="46" fill="url(#orb)" />
                <circle cx="310" cy="70" r="36" fill="url(#orb)" />
                <circle cx="320" cy="200" r="52" fill="url(#orb)" />
                <circle cx="120" cy="210" r="28" fill="url(#orb)" />
                <path
                  d="M90 90 L310 70 L320 200 L120 210 Z"
                  fill="none"
                  stroke="rgba(255,255,255,0.35)"
                  strokeWidth="2"
                />
                <circle cx="200" cy="140" r="12" fill="rgba(255,255,255,0.7)" />
                <circle cx="210" cy="110" r="6" fill="rgba(255,255,255,0.6)" />
                <circle cx="180" cy="170" r="8" fill="rgba(255,255,255,0.6)" />
              </svg>
              <div className="brand-caption">
                Secure RBAC system built with Django, React and JWT authentication.
              </div>
            </div>

            <div className="brand-metrics">
              <div className="metric-card">
                <span className="metric-label">Secure Access</span>
                <span className="metric-value">JWT + RBAC</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Unified Records</span>
                <span className="metric-value">Verified Members</span>
              </div>
            </div>
          </div>
        </aside>

        <section className="login-panel">
          <div className="login-card">
            <div className="login-body">
              <div className="login-topbar">
                <div className="login-logo">
                  <img src={aisuLogo} alt="AISU logo" />
                </div>
                <button type="button" className="theme-toggle" onClick={toggleTheme}>
                  {theme === 'dark' ? 'Light mode' : 'Dark mode'}
                </button>
              </div>
              <div className="login-header-section">
                <h2>Welcome back</h2>
                <p>Sign in to continue to AISU Portal</p>
              </div>

              {error && (
                <div className="error-helper" role="alert">
                  <span className="error-icon">⚠️</span>
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="login-form">
                <div className={`form-group ${focusedField === 'username' ? 'focused' : ''} ${error ? 'has-error' : ''}`}>
                  <label htmlFor="username">
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

                <div className={`form-group ${focusedField === 'password' ? 'focused' : ''} ${error ? 'has-error' : ''}`}>
                  <label htmlFor="password">
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
                      {showPassword ? '👁‍🗨️' : '👁️'}
                    </button>
                  </div>
                </div>

                <div className="form-options">
                  <label className="remember-me">
                    <input type="checkbox" />
                    <span className="checkmark"></span>
                    Remember me
                  </label>
                  <Link to="/forgot-password" className="forgot-password">Forgot password?</Link>
                </div>

                <button
                  type="submit"
                  className={`login-button ${loading ? 'loading' : ''}`}
                  disabled={loading}
                  onClick={handleRipple}
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

              <div className="login-meta">
                <div className="last-login">Last login: {lastLoginText}</div>
              </div>

              <div className="alt-signin">
                <div className="alt-divider">
                  <span>Or continue with</span>
                </div>
                <div className="alt-actions">
                  <button type="button" className="alt-button" disabled>
                    Continue with SSO (Coming soon)
                  </button>
                </div>
              </div>

              <div className="login-footer">
                <p>Secured with JWT Authentication</p>
              </div>

              <div className="trust-indicators">
                <div className="trust-item">
                  <span className="trust-icon" aria-hidden="true">🔒</span>
                  <span>Secure login</span>
                </div>
                <div className="trust-item">
                  <span className="trust-icon" aria-hidden="true">🏛️</span>
                  <span>Official internal system</span>
                </div>
                <div className="trust-item">
                  <span className="trust-icon" aria-hidden="true">🧭</span>
                  <span>Role-based access routing</span>
                </div>
                <div className="trust-version">Version: v1.0</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Login;
