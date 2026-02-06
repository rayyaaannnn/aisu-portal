import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store the JWT tokens in localStorage
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        
        // Fetch user info to get role for role-based redirect
        const userInfoResponse = await fetch('/accounts/user-info/', {
          headers: {
            'Authorization': `Bearer ${data.access}`,
          },
        });
        
        let redirectPath = '/dashboard';
        if (userInfoResponse.ok) {
          const userData = await userInfoResponse.json();
          localStorage.setItem('user', JSON.stringify(userData));
          
          // Role-based redirect (matching Django urls.py)
          switch (userData.role) {
            case 'super_admin':
              redirectPath = '/dashboard';
              break;
            case 'it_team':
              redirectPath = '/dashboard';
              break;
            case 'state_team':
              redirectPath = '/dashboard';
              break;
            case 'district_team':
              redirectPath = '/dashboard';
              break;
            default:
              redirectPath = '/dashboard';
          }
        }
        
        // Redirect to dashboard
        navigate(redirectPath);
      } else {
        // Handle error
        if (data.detail) {
          setError(data.detail);
        } else if (data.non_field_errors) {
          setError(data.non_field_errors[0]);
        } else {
          setError('Login failed. Please check your credentials.');
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>AISU Portal</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="login-footer">
          <p>Powered by AISU Portal</p>
        </div>
      </div>
    </div>
  );
}

export default Login;

