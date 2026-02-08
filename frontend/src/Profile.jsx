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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
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
        console.error('Failed to fetch profile:', response.status, response.statusText);
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Network error:', err);
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
    setIsSubmitting(true);

    // Validate email format if provided
    if (formData.email.trim() && formData.email.trim().length > 0) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        setIsSubmitting(false);
        return;
      }
    }

    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('Authentication token not found');
        setIsSubmitting(false);
        return;
      }

      let response;
      if (selectedFile) {
        // Create FormData object for file upload
        const formDataToSend = new FormData();
        
        // Append regular form fields
        Object.keys(formData).forEach(key => {
          if (formData[key] !== null && formData[key] !== undefined && key !== 'photo_url') {
            formDataToSend.append(key, formData[key]);
          }
        });

        // Append file if selected
        formDataToSend.append('photo', selectedFile);

        response = await fetch('/accounts/profile/update/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formDataToSend,
        });
      } else {
        // Use JSON for text-only updates
        response = await fetch('/accounts/profile/update/', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            first_name: formData.first_name,
            last_name: formData.last_name,
            email: formData.email,
            state: formData.state,
            district: formData.district,
            phone: formData.phone,
            photo_url: formData.photo_url, // Keep existing photo URL if no new file
          }),
        });
      }

      if (response.ok) {
        // Handle response - when using FormData, the response should still be JSON
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
        // Clear file selection after successful update
        setSelectedFile(null);
        setPreviewUrl(null);

        // Update user data in localStorage to reflect changes across the app
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        userData.first_name = data.profile.first_name;
        userData.last_name = data.profile.last_name;
        userData.email = data.profile.email;
        userData.state = data.profile.state;
        userData.district = data.profile.district;
        userData.phone = data.profile.phone;
        userData.photo_url = data.profile.photo_url;
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        // Handle error response - might be JSON or plain text
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If response is not JSON, try to get text
          const errorText = await response.text();
          errorData = { error: errorText };
        }
        setError(errorData.error || 'Failed to update profile');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.match('image.*')) {
        setError('Please select an image file (JPEG, PNG, etc.)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size exceeds 5MB limit');
        return;
      }

      // Set the selected file
      setSelectedFile(file);

      // Create a preview URL
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreviewUrl(event.target.result);
      };
      reader.readAsDataURL(file);

      // Clear any previous error
      setError('');
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
    // Reset file selection and preview
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  if (loading) {
    return (
      <SimplePage title="Profile" subtitle="Your account details">
        <div className="profile-content">
          <div className="profile-view" style={{textAlign: 'center', padding: '40px 20px'}}>
            <div className="loading-state">
              <div className="loading-spinner" style={{width: '40px', height: '40px', border: '4px solid rgba(255,255,255,0.1)', borderTop: '4px solid var(--accent-500)', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px'}}></div>
              <p style={{color: 'var(--text-muted)', fontSize: '14px'}}>Loading profile...</p>
            </div>
          </div>
        </div>
      </SimplePage>
    );
  }

  return (
    <>
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <SimplePage title="Profile" subtitle="Manage your account information">
      <div className="profile-content">
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
          
          <div className="profile-header-info" style={{textAlign: 'center', marginBottom: '20px'}}>
            <h2 style={{margin: '8px 0', fontSize: '24px', color: '#fff'}}>{profile?.first_name} {profile?.last_name}</h2>
            <p style={{margin: '4px 0', color: 'var(--text-muted)'}}>@{profile?.username}</p>
            <span className={`role-tag ${profile?.role}`} style={{display: 'inline-block', marginTop: '8px', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
              {profile?.role?.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          {!isEditing ? (
            <div className="profile-view-mode">
              <div className="profile-section">
                <h3>Personal Information</h3>
                <div className="profile-info-grid">
                  <div className="profile-info-item">
                    <div className="profile-info-label">Full Name</div>
                    <div className="profile-info-value">
                      {profile?.first_name} {profile?.last_name || 'Not specified'}
                    </div>
                  </div>
                  <div className="profile-info-item">
                    <div className="profile-info-label">Email Address</div>
                    <div className="profile-info-value">{profile?.email}</div>
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <h3>Location Information</h3>
                <div className="profile-info-grid">
                  <div className="profile-info-item">
                    <div className="profile-info-label">State</div>
                    <div className="profile-info-value">{profile?.state || 'Not specified'}</div>
                  </div>
                  <div className="profile-info-item">
                    <div className="profile-info-label">District</div>
                    <div className="profile-info-value">{profile?.district || 'Not specified'}</div>
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <h3>Contact Information</h3>
                <div className="profile-info-grid">
                  <div className="profile-info-item">
                    <div className="profile-info-label">Phone Number</div>
                    <div className="profile-info-value">{profile?.phone || 'Not specified'}</div>
                  </div>
                  <div className="profile-info-item">
                    <div className="profile-info-label">Photo</div>
                    <div className="profile-info-value">
                      {profile?.photo_url ? (
                        <a href={profile.photo_url} target="_blank" rel="noopener noreferrer" style={{color: 'var(--accent-500)', textDecoration: 'underline'}}>
                          View Photo
                        </a>
                      ) : (
                        'Not set'
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <h3>Account Information</h3>
                <div className="profile-info-grid">
                  <div className="profile-info-item">
                    <div className="profile-info-label">Username</div>
                    <div className="profile-info-value">{profile?.username}</div>
                  </div>
                  <div className="profile-info-item">
                    <div className="profile-info-label">Role</div>
                    <div className="profile-info-value">
                      <span className={`role-tag ${profile?.role}`}>
                        {profile?.role?.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="profile-info-item">
                    <div className="profile-info-label">Member Since</div>
                    <div className="profile-info-value">
                      {profile?.date_joined
                        ? new Date(profile.date_joined).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })
                        : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="profile-actions">
                <button
                  type="button"
                  onClick={() => setIsEditing(true)}
                  className="profile-action-btn"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="profile-form">
              <div className="form-section">
                <h2>Personal Information</h2>
                <div className="form-row">
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
                </div>
                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter email address"
                  />
                </div>
              </div>

              <div className="form-section">
                <h2>Location Information</h2>
                <div className="form-row">
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

              <div className="form-section">
                <h2>Contact Information</h2>
                <div className="form-row">
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder="Enter phone number"
                    />
                  </div>
                  <div className="form-group">
                    <label>Upload Photo</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                    {previewUrl && (
                      <div style={{marginTop: '10px'}}>
                        <p>Preview:</p>
                        <img 
                          src={previewUrl} 
                          alt="Preview" 
                          style={{width: '100px', height: '100px', objectFit: 'cover', borderRadius: '8px', border: '1px solid var(--border-soft)'}}
                        />
                      </div>
                    )}
                    {formData.photo_url && !previewUrl && (
                      <div style={{marginTop: '10px'}}>
                        <p>Current Photo:</p>
                        <img 
                          src={formData.photo_url} 
                          alt="Current" 
                          style={{width: '100px', height: '100px', objectFit: 'cover', borderRadius: '8px', border: '1px solid var(--border-soft)'}}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-button" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Save Changes'}
                </button>
                <button type="button" onClick={handleCancel} className="cancel-button" disabled={isSubmitting}>
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </SimplePage>
    </>
  );
}

export default Profile;

