import React, { useState, useEffect } from 'react';
import './DesignationsList.css';

/**
 * DesignationsList - Component that displays designations grouped by level
 * 
 * Features:
 * - Fetches designations from /api/designations/
 * - Groups by level (National, State, District, Mandal, College)
 * - Expandable cards with name, department, "View Details" button
 * - Modal with full details on button click
 */
function DesignationsList() {
  const [designations, setDesignations] = useState([]);
  const [groupedDesignations, setGroupedDesignations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDesignation, setSelectedDesignation] = useState(null);
  const [expandedLevels, setExpandedLevels] = useState({});

  const LEVEL_ORDER = ['national', 'state', 'district', 'mandal', 'college'];
  const LEVEL_LABELS = {
    national: 'National',
    state: 'State',
    district: 'District',
    mandal: 'Mandal',
    college: 'College'
  };

  useEffect(() => {
    fetchDesignations();
  }, []);

  const fetchDesignations = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('/accounts/designations/', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch designations');
      }

      const data = await response.json();
      setDesignations(data);
      groupByLevel(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching designations:', err);
    } finally {
      setLoading(false);
    }
  };

  const groupByLevel = (designations) => {
    const grouped = {};
    designations.forEach((designation) => {
      const level = designation.level;
      if (!grouped[level]) {
        grouped[level] = [];
      }
      grouped[level].push(designation);
    });
    setGroupedDesignations(grouped);
    // Expand all levels by default
    const initialExpanded = {};
    LEVEL_ORDER.forEach((level) => {
      initialExpanded[level] = true;
    });
    setExpandedLevels(initialExpanded);
  };

  const toggleLevel = (level) => {
    setExpandedLevels((prev) => ({
      ...prev,
      [level]: !prev[level],
    }));
  };

  const openModal = (designation) => {
    setSelectedDesignation(designation);
  };

  const closeModal = () => {
    setSelectedDesignation(null);
  };

  if (loading) {
    return (
      <div className="designations-container">
        <div className="loading">Loading designations...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="designations-container">
        <div className="error-message">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="designations-container">
      <h1 className="designations-title">Organizational Designations</h1>
      
      {LEVEL_ORDER.map((level) => {
        const levelDesignations = groupedDesignations[level] || [];
        if (levelDesignations.length === 0) return null;

        return (
          <div key={level} className="designation-level-section">
            <div 
              className="level-header"
              onClick={() => toggleLevel(level)}
            >
              <h2>{LEVEL_LABELS[level]} Level</h2>
              <span className={`expand-icon ${expandedLevels[level] ? 'expanded' : ''}`}>
                ▼
              </span>
            </div>
            
            {expandedLevels[level] && (
              <div className="designation-cards">
                {levelDesignations.map((designation) => (
                  <div key={designation.id} className="designation-card">
                    <div className="designation-card-header">
                      <h3>{designation.name}</h3>
                      {designation.department && (
                        <span className="department-badge">
                          {designation.department}
                        </span>
                      )}
                    </div>
                    <button 
                      className="view-details-btn"
                      onClick={() => openModal(designation)}
                    >
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Modal */}
      {selectedDesignation && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            
            <div className="modal-header">
              <h2>{selectedDesignation.name}</h2>
              <span className="level-badge">
                {selectedDesignation.level_display}
              </span>
              {selectedDesignation.department && (
                <span className="department-badge large">
                  {selectedDesignation.department}
                </span>
              )}
            </div>

            <div className="modal-body">
              {selectedDesignation.description && (
                <div className="modal-section">
                  <h4>Description</h4>
                  <p>{selectedDesignation.description}</p>
                </div>
              )}

              {selectedDesignation.responsibilities && (
                <div className="modal-section">
                  <h4>Responsibilities</h4>
                  <p>{selectedDesignation.responsibilities}</p>
                </div>
              )}

              {selectedDesignation.authority && (
                <div className="modal-section">
                  <h4>Authority</h4>
                  <p>{selectedDesignation.authority}</p>
                </div>
              )}

              {selectedDesignation.accountability && (
                <div className="modal-section">
                  <h4>Accountability</h4>
                  <p>{selectedDesignation.accountability}</p>
                </div>
              )}

              {selectedDesignation.parent_name && (
                <div className="modal-section">
                  <h4>Reports To</h4>
                  <p>{selectedDesignation.parent_name}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DesignationsList;
