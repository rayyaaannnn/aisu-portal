import React, { useState, useEffect } from 'react';
import { loginLogService } from './services/loginLogService';
import SimplePage from './SimplePage';
import './LoginLogs.css';

function LoginLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    limit: 50,
    offset: 0,
    totalCount: 0
  });

  useEffect(() => {
    fetchLoginLogs();
  }, [pagination.offset, pagination.limit]);

  const fetchLoginLogs = async () => {
    try {
      setLoading(true);
      const data = await loginLogService.getLoginLogs(pagination.limit, pagination.offset);
      setLogs(data.logs);
      setPagination(prev => ({
        ...prev,
        totalCount: data.total_count
      }));
      setError('');
    } catch (err) {
      setError(err.error || 'Failed to fetch login logs');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newOffset) => {
    if (newOffset >= 0 && newOffset < pagination.totalCount) {
      setPagination(prev => ({
        ...prev,
        offset: newOffset
      }));
    }
  };

  const totalPages = Math.ceil(pagination.totalCount / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  if (loading) {
    return (
      <div className="login-logs-container">
        <div className="loading">Loading login logs...</div>
      </div>
    );
  }

  return (
    <SimplePage title="Login Logs" subtitle="Track user login activities">
      <div className="login-logs-container">
        <header className="page-header">
          <h1>Login Logs</h1>
        </header>

        {error && <div className="error-message">{error}</div>}

        <div className="logs-table-container">
          <table className="logs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>IP Address</th>
                <th>User Agent</th>
                <th>Timestamp</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.username}</td>
                  <td>{log.ip_address || 'N/A'}</td>
                  <td>{log.user_agent ? log.user_agent.substring(0, 50) + '...' : 'N/A'}</td>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${log.success ? 'success' : 'failed'}`}>
                      {log.success ? 'Success' : 'Failed'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="pagination">
          <button
            onClick={() => handlePageChange(pagination.offset - pagination.limit)}
            disabled={currentPage <= 1}
            className="pagination-btn"
          >
            Previous
          </button>
          
          <span className="pagination-info">
            Page {currentPage} of {totalPages} ({pagination.totalCount} total records)
          </span>
          
          <button
            onClick={() => handlePageChange(pagination.offset + pagination.limit)}
            disabled={currentPage >= totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      </div>
    </SimplePage>
  );
}

export default LoginLogs;