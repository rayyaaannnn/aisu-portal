import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Profile - Component for users to view and edit their profile
 */
function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  // Form state
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
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        setSuccess('Profile updated successfully!');
        setIsEditing(false);

        // Update localStorage user data
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
      <div className="profile-container">
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <header className="page-header">
        <h1>My Profile</h1>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="edit-profile-button"
          >
            Edit Profile
          </button>
        )}
      </header>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="profile-content">
        {isEditing ? (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-section">
              <h2>Personal Information</h2>

              <div className="form-row">
                <div className="form-group">
                  <label>First Name:</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label>Last Name:</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Email:</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-section">
              <h2>Location Information</h2>

              <div className="form-row">
                <div className="form-group">
                  <label>State:</label>
                  <input
                    type="text"
                    name="state"
                    value={formData.state}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label>District:</label>
                  <input
                    type="text"
                    name="district"
                    value={formData.district}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Phone:</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-section">
              <h2>Additional Information</h2>

              <div className="form-group">
                <label>Photo URL:</label>
                <input
                  type="url"
                  name="photo_url"
                  value={formData.photo_url}
                  onChange={handleInputChange}
                  placeholder="https://example.com/photo.jpg"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-button">
                Save Changes
              </button>
              <button type="button" onClick={handleCancel} className="cancel-button">
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="profile-view">
            <div className="profile-avatar">
              {profile?.photo_url ? (
                <img src={profile.photo_url} alt="Profile" />
              ) : (
                <div className="avatar-placeholder">
                  {profile?.first_name?.[0] || profile?.username?.[0] || 'U'}
                </div>
              )}
            </div>

            <div className="profile-details">
              <div className="detail-section">
                <h2>Personal Information</h2>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Username:</label>
                    <span>{profile?.username}</span>
                  </div>
                  <div className="detail-item">
                    <label>Full Name:</label>
                    <span>{profile?.first_name} {profile?.last_name}</span>
                  </div>
                  <div className="detail-item">
                    <label>Email:</label>
                    <span>{profile?.email}</span>
                  </div>
                  <div className="detail-item">
                    <label>Role:</label>
                    <span>{profile?.role?.replace('_', ' ').toUpperCase()}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h2>Location Information</h2>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>State:</label>
                    <span>{profile?.state || 'Not specified'}</span>
                  </div>
                  <div className="detail-item">
                    <label>District:</label>
                    <span>{profile?.district || 'Not specified'}</span>
                  </div>
                  <div className="detail-item">
                    <label>Phone:</label>
                    <span>{profile?.phone || 'Not specified'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
