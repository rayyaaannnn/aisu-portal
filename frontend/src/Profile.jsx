import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SimplePage from './SimplePage';
import './Dashboard.css';

function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    state: '',
    district: '',
    phone: '',
    photo_url: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        navigate('/');
        return;
      }

      const response = await fetch('/accounts/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          email: data.email || '',
          state: data.state || '',
          district: data.district || '',
          phone: data.phone || '',
          photo_url: data.photo_url || ''
        });
      } else {
        setError('Failed to fetch profile');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('/accounts/profile/update/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data.profile);
        setFormData({
          first_name: data.profile.first_name || '',
          last_name: data.profile.last_name || '',
          email: data.profile.email || '',
          state: data.profile.state || '',
          district: data.profile.district || '',
          phone: data.profile.phone || '',
          photo_url: data.profile.photo_url || ''
        });
        setSuccess(data.message || 'Profile updated successfully!');
        setIsEditing(false);

        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        userData.first_name = formData.first_name;
        userData.last_name = formData.last_name;
        userData.email = formData.email;
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update profile');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      first_name: profile?.first_name || '',
      last_name: profile?.last_name || '',
      email: profile?.email || '',
      state: profile?.state || '',
      district: profile?.district || '',
      phone: profile?.phone || '',
      photo_url: profile?.photo_url || ''
    });
  };

  if (loading) {
    return (
      <SimplePage title="Profile" subtitle="Your account details">
        <div className="profile-container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading profile...</p>
          </div>
        </div>
      </SimplePage>
    );
  }

  return (
    <SimplePage title="Profile" subtitle="Manage your account information">
      <div className="profile-container">
        <div className="profile-header-card">
          <div className="profile-header-content">
            <div className="profile-avatar-large">
              {profile?.photo_url ? (
                <img src={profile.photo_url} alt="Profile" />
              ) : (
                <div className="avatar-initial">
                  {profile?.first_name?.[0] || profile?.username?.[0] || 'U'}
                </div>
              )}
            </div>
            <div className="profile-header-info">
              <h2>{profile?.first_name} {profile?.last_name}</h2>
              <p className="profile-username">@{profile?.username}</p>
              <span className={`profile-role-badge ${profile?.role}`}>
                {profile?.role?.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {error && (
          <div className="profile-message error">
            {error}
          </div>
        )}
        {success && (
          <div className="profile-message success">
            {success}
          </div>
        )}

        <div className="profile-content-card">
          {isEditing ? (
            <form onSubmit={handleSubmit} className="profile-edit-form">
              <div className="profile-section">
                <div className="section-header">
                  <h3>Personal Information</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      placeholder="Enter first name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      placeholder="Enter last name"
                    />
                  </div>
                  <div className="form-group full-width">
                    <label>Email Address</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      placeholder="Enter email address"
                    />
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <div className="section-header">
                  <h3>Location Information</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>State</label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleInputChange}
                      placeholder="Enter state"
                    />
                  </div>
                  <div className="form-group">
                    <label>District</label>
                    <input
                      type="text"
                      name="district"
                      value={formData.district}
                      onChange={handleInputChange}
                      placeholder="Enter district"
                    />
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <div className="section-header">
                  <h3>Contact Information</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group full-width">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder="Enter phone number"
                    />
                  </div>
                  <div className="form-group full-width">
                    <label>Photo URL</label>
                    <input
                      type="url"
                      name="photo_url"
                      value={formData.photo_url}
                      onChange={handleInputChange}
                      placeholder="https://example.com/photo.jpg"
                    />
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <div className="section-header">
                  <h3>Account Information</h3>
                </div>
                <div className="account-info-grid">
                  <div className="info-item">
                    <span className="info-label">Username</span>
                    <span className="info-value">{profile?.username}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Role</span>
                    <span className="info-value role">
                      {profile?.role?.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Member Since</span>
                    <span className="info-value">
                      {profile?.date_joined
                        ? new Date(profile.date_joined).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="form-actions-bar">
                <button type="submit" className="submit-button">
                  Save Changes
                </button>
                <button type="button" onClick={handleCancel} className="cancel-button">
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-view-mode">
              <div className="display-section">
                <div className="section-header">
                  <h3>Personal Information</h3>
                </div>
                <div className="info-grid">
                  <div className="info-card">
                    <span className="info-label">Full Name</span>
                    <span className="info-value">
                      {profile?.first_name} {profile?.last_name || 'Not specified'}
                    </span>
                  </div>
                  <div className="info-card">
                    <span className="info-label">Email Address</span>
                    <span className="info-value">{profile?.email}</span>
                  </div>
                </div>
              </div>

              <div className="display-section">
                <div className="section-header">
                  <h3>Location Information</h3>
                </div>
                <div className="info-grid">
                  <div className="info-card">
                    <span className="info-label">State</span>
                    <span className="info-value">{profile?.state || 'Not specified'}</span>
                  </div>
                  <div className="info-card">
                    <span className="info-label">District</span>
                    <span className="info-value">{profile?.district || 'Not specified'}</span>
                  </div>
                </div>
              </div>

              <div className="display-section">
                <div className="section-header">
                  <h3>Contact Information</h3>
                </div>
                <div className="info-grid">
                  <div className="info-card">
                    <span className="info-label">Phone Number</span>
                    <span className="info-value">{profile?.phone || 'Not specified'}</span>
                  </div>
                  <div className="info-card">
                    <span className="info-label">Photo</span>
                    <span className="info-value photo">
                      {profile?.photo_url ? (
                        <a href={profile.photo_url} target="_blank" rel="noopener noreferrer" className="photo-link">
                          View Photo
                        </a>
                      ) : (
                        'Not set'
                      )}
                    </span>
                  </div>
                </div>
              </div>

              <div className="display-section">
                <div className="section-header">
                  <h3>Account Information</h3>
                </div>
                <div className="account-info-grid">
                  <div className="info-card full">
                    <div className="info-row">
                      <span className="info-label">Username</span>
                      <span className="info-value">{profile?.username}</span>
                    </div>
                  </div>
                  <div className="info-card full">
                    <div className="info-row">
                      <span className="info-label">Role</span>
                      <span className="info-value">
                        <span className={`role-tag ${profile?.role}`}>
                          {profile?.role?.replace('_', ' ').toUpperCase()}
                        </span>
                      </span>
                    </div>
                  </div>
                  <div className="info-card full">
                    <div className="info-row">
                      <span className="info-label">Member Since</span>
                      <span className="info-value">
                        {profile?.date_joined
                          ? new Date(profile.date_joined).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })
                          : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="form-actions-bar">
                <button
                  type="button"
                  onClick={() => setIsEditing(true)}
                  className="profile-edit-btn"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </SimplePage>
  );
}

export default Profile;

