import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SimplePage from './SimplePage';

/**
 * UserManagement - Component for Super Admin to manage users
 * Features: List users, Add new user, Edit user, Delete user
 */
function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const navigate = useNavigate();

  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'district_team',
    state: '',
    district: ''
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        navigate('/');
        return;
      }

      const response = await fetch('/accounts/users/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || data);
      } else if (response.status === 403) {
        setError('Access denied. Super admin privileges required.');
      } else {
        setError('Failed to fetch users');
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
    setLoading(true);

    try {
      const token = localStorage.getItem('accessToken');
      const url = editingUser ? `/accounts/users/${editingUser.id}/edit/` : '/accounts/users/add/';
      const method = editingUser ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await fetchUsers(); // Refresh the list
        setShowAddForm(false);
        setEditingUser(null);
        setFormData({
          username: '',
          email: '',
          password: '',
          role: 'district_team',
          state: '',
          district: ''
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to save user');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // Don't pre-fill password
      role: user.role || 'district_team',
      state: user.state || '',
      district: user.district || ''
    });
    setShowAddForm(true);
  };

  const handleDelete = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`/accounts/users/${userId}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchUsers(); // Refresh the list
      } else {
        setError('Failed to delete user');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const cancelForm = () => {
    setShowAddForm(false);
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'district_team',
      state: '',
      district: ''
    });
  };

  if (loading) {
    return (
      <div className="user-management-container">
        <div className="loading">Loading users...</div>
      </div>
    );
  }

  return (
    <SimplePage title="User Management" subtitle="Manage members and roles">
      <div className="user-management-container">
        <header className="page-header">
          <h1>User Management</h1>
          <button
            onClick={() => setShowAddForm(true)}
            className="add-user-button"
          >
            Add New User
          </button>
        </header>

        {error && <div className="error-message">{error}</div>}

        {showAddForm && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h2>{editingUser ? 'Edit User' : 'Add New User'}</h2>
              <form onSubmit={handleSubmit} className="user-form">
                <div className="form-group">
                  <label>Username:</label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    disabled={!!editingUser} // Can't change username when editing
                  />
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

                {!editingUser && (
                  <div className="form-group">
                    <label>Password:</label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required={!editingUser}
                    />
                  </div>
                )}

                <div className="form-group">
                  <label>Role:</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="district_team">District Team</option>
                    <option value="state_team">State Team</option>
                    <option value="it_team">IT Team</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>

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

                <div className="form-actions">
                  <button type="submit" className="submit-button">
                    {editingUser ? 'Update User' : 'Create User'}
                  </button>
                  <button type="button" onClick={cancelForm} className="cancel-button">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>State</th>
                <th>District</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.role || 'N/A'}</td>
                  <td>{user.state || '-'}</td>
                  <td>{user.district || '-'}</td>
                  <td>
                    <button
                      onClick={() => handleEdit(user)}
                      className="edit-button"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(user.id, user.username)}
                      className="delete-button"
                      disabled={(() => {
                        try {
                          const stored = JSON.parse(localStorage.getItem('user'));
                          return stored?.username === user.username;
                        } catch {
                          return false;
                        }
                      })()}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </SimplePage>
  );
}

export default UserManagement;
