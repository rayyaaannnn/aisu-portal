import React, { useState, useEffect } from 'react';
import './DesignationsList.css';
import SimplePage from './SimplePage';

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

  const DRAR_LEVELS = {
    national: [
      'National President',
      'National Vice-President',
      'National General Secretary',
      'National Joint Secretary',
      'National Additional Joint Secretary (1 & 2)',
      'National Organizing Secretary',
      'National Additional Organizing Secretary (max 2)',
      'National Coordinator',
      'National Convenor / Co-Convenor / General Secretary / Secretary (Social Media, Press, IT Cell, Legal)',
      'National Members (Social Media, Press, IT, Legal)',
      'National Graphic Designer',
      'National Spokesperson',
      'National Incharge',
      'Regional Incharge (per region)'
    ],
    state: [
      'State President',
      'State Vice-President',
      'State General Secretary',
      'State Joint Secretary',
      'State Additional Joint Secretary',
      'State Organizing Secretary',
      'State Additional Organizing Secretary',
      'State Coordinator',
      'State Convenor / General Secretary / Members (Social Media, Press, IT, Legal)',
      'State Graphic Designer',
      'State Spokesperson',
      'Zonal Incharge'
    ],
    district: [
      'District President',
      'District Vice-President',
      'District General Secretary',
      'District Joint Secretary',
      'District Organizing Secretary',
      'District Coordinator (Administration / Social Media / Press / IT / Legal)',
      'District Graphic Designer',
      'District Members (Social Media, Press, IT, Legal)',
      'District Spokesperson',
      'Divisional Incharge'
    ],
    mandal: [
      'Mandal President',
      'Mandal Vice-President',
      'Mandal General Secretary',
      'Mandal Joint Secretary',
      'Mandal Organizing Secretary',
      'Mandal Coordinator',
      'Mandal Spokesperson'
    ],
    college: [
      'College Head',
      'College Ambassador',
      'College Member'
    ]
  };

  const DRAR_DETAILS = [
    {
      title: 'National President',
      level: 'National',
      responsibilities: [
        'Supreme executive authority; guides, coordinates, supervises AISU.',
        'Chairs NEC and National Council; can take emergency decisions subject to NEC ratification within 30 days.',
        'May propose/approve constitutional amendments; create or dissolve national departments/cells.',
        'Interprets constitution and resolves disputes; ex-officio chair of all national trusts/departments.'
      ],
      authority: 'Ultimate authority over all departments; emergency powers per Art. IX; structural changes per Art. X & XIX.',
      accountability: 'Accountable to NEC and National Council.'
    },
    {
      title: 'National Vice-President (max 5)',
      level: 'National',
      responsibilities: [
        'Deputy leadership for the President; assists in all executive functions.',
        'Acts as President when absent/incapacitated.',
        'Leads assigned departments or regions and liaises with State Executives.'
      ],
      accountability: 'Reports to National President and NEC.'
    },
    {
      title: 'National General Secretary',
      level: 'National',
      responsibilities: [
        'Chief administrator: day-to-day functioning and coordination across departments/states.',
        'Convenes NEC/NC meetings as instructed; keeps minutes, resolutions, orders.',
        'Issues official orders with NEC/President approval; submits annual admin/financial reports.'
      ],
      accountability: 'Reports to NEC and National President/Vice-President.'
    },
    {
      title: 'National Joint Secretary & Additional Joint Secretaries',
      level: 'National',
      responsibilities: [
        'Assist General Secretary with national programs, documentation, inter-department communication.',
        'Draft reports, coordinate logistics; act on delegated tasks.'
      ],
      accountability: 'Report to General Secretary / President / Vice-President / NEC.'
    },
    {
      title: 'National Organizing Secretary',
      level: 'National',
      responsibilities: [
        'Lead nationwide mobilization, outreach, and membership drives.',
        'Build/monitor state and district organizing structures; run training workshops.',
        'Recommend structural reforms; direct state/district organizing secretaries.'
      ],
      accountability: 'Reports to President / Vice-President / General Secretary and NEC.'
    },
    {
      title: 'National Additional Organizing Secretaries (max 2)',
      level: 'National',
      responsibilities: [
        'Assist Organizing Secretary on region-specific campaigns.',
        'Conduct outreach and follow-ups; monitor institutional activities; support logistics.'
      ],
      accountability: 'Report to National Organizing Secretary / General Secretary / President / Vice-President.'
    },
    {
      title: 'National Coordinator',
      level: 'National',
      responsibilities: [
        'Bridge departments and field ops; collect data to build dashboards.',
        'Draft implementation blueprints; support inter-department campaigns.',
        'Run coordination meetings with department heads.'
      ],
      accountability: 'Reports to General Secretary / Vice-President / President and NEC.'
    },
    {
      title: 'Dept. Convenor / Co-Convenor (Social Media, Press, IT, Legal)',
      level: 'National',
      responsibilities: [
        'Executive heads and policy formulators for their departments.',
        'Lead strategy, supervision, and inter-department coordination.',
        'Dept-specific: Legal filings & compliance; Social Media strategy & safety; Press statements & archives; IT security & platforms.'
      ],
      authority: 'May nominate state/lower counterparts with NEC consent; subject to NEC audit and possible dissolution.',
      accountability: 'Quarterly reports to NEC; oversight by President/Vice-President/General Secretary.'
    },
    {
      title: 'Dept. General Secretary (National Depts)',
      level: 'National',
      responsibilities: [
        'Operational head executing convenor’s strategy; supervise secretaries.',
        'Maintain schedules, analytics, archives; ensure maintenance/security (IT) and compliance (Legal).'
      ],
      accountability: 'Reports monthly to Convenor; reviewed by NEC.'
    },
    {
      title: 'Dept. Secretary (National Depts)',
      level: 'National',
      responsibilities: [
        'Execute directives; maintain logs; assist events and daily activities.',
        'Dept-specific execution (posting, drafting, web updates, legal files).'
      ],
      accountability: 'Reports to Dept. General Secretary; reviewed under Art. X-VI.'
    },
    {
      title: 'Dept. Member (National Depts)',
      level: 'National',
      responsibilities: [
        'Support research, content, operations; only 2–3 members per dept per level.',
        'Lower-level role holders automatically count as members at upper level.'
      ],
      accountability: 'Report to Secretary/General Secretary; monitored via reviews.'
    },
    {
      title: 'National Graphic Designer',
      level: 'National',
      responsibilities: [
        'Design all media assets; maintain template repository; support events.',
        'Work with Social Media/Press/IT for brand consistency.'
      ],
      authority: 'May suggest visual improvements; can assign juniors with approval.',
      accountability: 'Reports to Social Media Convenor and NEC/leadership.'
    },
    {
      title: 'National Spokesperson',
      level: 'National',
      responsibilities: [
        'Official AISU representative for national press/media.',
        'Issue statements, handle debates, counter misinformation.'
      ],
      authority: 'Needs leadership clearance for sensitive comments.',
      accountability: 'Reports to President/Vice-President/General Secretary and NEC.'
    },
    {
      title: 'National Incharge',
      level: 'National',
      responsibilities: [
        'Cross-domain admin/operational support; resolve urgent issues.',
        'Prepare reports, evaluations; support restructuring of inactive committees.',
        'Central point for emergency decisions when authorized.'
      ],
      authority: 'May exercise administrative/financial/quasi-judicial powers with approval of any two among President, VP, General Secretary.',
      accountability: 'Reports to President, VP, General Secretary, and NEC.'
    },
    {
      title: 'Regional Incharge',
      level: 'National',
      responsibilities: [
        'Operational authority for assigned region; monitor state/district performance.',
        'Conduct visits, reviews, grievance redressal; recommend promotions/discipline.'
      ],
      authority: 'May issue regional circulars and request compliance reports.',
      accountability: 'Reports to President/VP/General Secretary, National Organizing Secretary, and National Incharge.'
    },
    {
      title: 'State President',
      level: 'State',
      responsibilities: [
        'Apex state authority; presides over State Council/SEC.',
        'Lead state policy, finance integrity, liaison with NEC; emergency decisions subject to SEC/NEC ratification.'
      ],
      accountability: 'Reports to NEC; submits periodic and annual reports.'
    },
    {
      title: 'State Vice-President(s) (max 5)',
      level: 'State',
      responsibilities: [
        'Deputize for State President; lead departments/zones; represent state nationally.',
        'Convene meetings and approve departmental activities.'
      ],
      accountability: 'Reports to State President and SEC/NEC.'
    },
    {
      title: 'State General Secretary',
      level: 'State',
      responsibilities: [
        'Chief admin at state level; records policies/minutes; convenes SC/SEC.',
        'Inter-district coordination and grievance resolution; issue appointment/official orders.'
      ],
      accountability: 'Reports to State President, NEC, and National General Secretary.'
    },
    {
      title: 'State Joint Secretary & Additional Joint Secretary',
      level: 'State',
      responsibilities: [
        'Assist documentation, scheduling, reporting; liaison across departments; logistics for campaigns/events.'
      ],
      accountability: 'Report to State General Secretary/President/NEC.'
    },
    {
      title: 'State Organizing Secretary & Additional Organizing Secretary',
      level: 'State',
      responsibilities: [
        'Lead state mobilization drives and training; build district teams; supervise zonal campaigns.',
        'Direct District Organizing Secretaries; recommend structural changes.'
      ],
      accountability: 'Reports to State President/SEC/NEC and National Organizing Secretary.'
    },
    {
      title: 'State Coordinator',
      level: 'State',
      responsibilities: [
        'Monitor inter-department performance; draft state implementation plans from district feedback.',
        'Maintain dashboards; call coordination meetings.'
      ],
      accountability: 'Reports to State General Secretary/President/NEC.'
    },
    {
      title: 'Dept. Convenor / General Secretary / Members (State Depts)',
      level: 'State',
      responsibilities: [
        'Strategize and supervise state Social Media/Press/IT/Legal departments.',
        'Quarterly reports to SEC/NEC; execute operations and compliance.',
        'Members execute campaigns/outreach/legal documentation (2–3 per dept per level; lower-level roles count upward).'
      ],
      accountability: 'Report to State President and national respective departments/NEC.'
    },
    {
      title: 'State Graphic Designer',
      level: 'State',
      responsibilities: [
        'Produce state-level campaign materials; support social media/press content.'
      ],
      accountability: 'Reports to Social Media Convenor / NEC / SEC.'
    },
    {
      title: 'State Spokesperson',
      level: 'State',
      responsibilities: [
        'Official state representative for media; issue statements with clearance; address press.'
      ],
      accountability: 'Reports to State President and SEC/NEC.'
    },
    {
      title: 'Zonal Incharge',
      level: 'State',
      responsibilities: [
        'Monitor districts in zone; run review meetings; bridge SEC and districts.',
        'Identify non-performing districts; coordinate zonal drives.'
      ],
      authority: 'May issue zone circulars after state approval; call compliance reports.',
      accountability: 'Reports to NEC/SEC/State Organizing Secretary/State General Secretary; 6-month progress reports.'
    },
    {
      title: 'District President',
      level: 'District',
      responsibilities: [
        'Apex district authority; presides DC/DEC; supervise programs and grievances.',
        'Issue district directives; form temporary committees.'
      ],
      accountability: 'Reports to State President/SEC/NEC/DEC; quarterly performance & financial reports.'
    },
    {
      title: 'District Vice-President(s) (max 3)',
      level: 'District',
      responsibilities: [
        'Assist District President; manage portfolios/zones; act as President when needed.'
      ],
      accountability: 'Reports to District President/General Secretary and NEC/SEC/DEC.'
    },
    {
      title: 'District General Secretary',
      level: 'District',
      responsibilities: [
        'Convene DEC; maintain district records and resolutions; coordinate with Mandals.',
        'Issue orders within district; monthly activity logs to SEC.'
      ],
      accountability: 'Reports to District President/DEC/SEC/NEC.'
    },
    {
      title: 'District Joint Secretary',
      level: 'District',
      responsibilities: [
        'Assist General Secretary with admin/communication; minutes, reports, liaison duties.'
      ],
      accountability: 'Reports to District General Secretary and NEC/SEC/DEC.'
    },
    {
      title: 'District Organizing Secretary',
      level: 'District',
      responsibilities: [
        'Plan membership drives and outreach; workshops; coordinate with Mandal Organizing Secretaries; monthly progress reports.'
      ],
      authority: 'May propose district structural changes; direct mandal organizing units.',
      accountability: 'Reports to NEC/SEC/DEC/State Organizing Secretary/District President.'
    },
    {
      title: 'District Coordinators (Admin/Social/Press/IT/Legal)',
      level: 'District',
      responsibilities: [
        'Oversee departmental tasks; provide district insights; monitor mandal coordinators.',
        'Organize department events/meetings.'
      ],
      accountability: 'Reports to District General Secretary and relevant State/National depts and NEC/SEC/DEC.'
    },
    {
      title: 'District Graphic Designer',
      level: 'District',
      responsibilities: [
        'Design district campaign material; collaborate with Social Media/Press; maintain archives.'
      ],
      accountability: 'Reports to District Social Media Coordinator and DEC/SEC/NEC.'
    },
    {
      title: 'District Spokesperson',
      level: 'District',
      responsibilities: [
        'Official district voice; releases/addresses media with approval; represent AISU locally.'
      ],
      accountability: 'Reports to District President & Press Coordinator / DEC / SEC / NEC.'
    },
    {
      title: 'Divisional Incharge',
      level: 'District',
      responsibilities: [
        'Supervise multiple mandals; field visits; training; consolidate reports; manage escalations.'
      ],
      authority: 'May recommend discipline or promotions at mandal level.',
      accountability: 'Reports to District Organizing Secretary / District General Secretary / DEC / SEC / NEC.'
    },
    {
      title: 'Mandal President',
      level: 'Mandal',
      responsibilities: [
        'Local executive authority; chair mandal meetings; implement district directives; represent AISU locally.'
      ],
      accountability: 'Reports to District President/General Secretary and executive committees (NEC/SEC/DEC/MEC).'
    },
    {
      title: 'Mandal Vice-President',
      level: 'Mandal',
      responsibilities: [
        'Support Mandal President; act interim; supervise projects.'
      ],
      accountability: 'Reports to Mandal President and executive committees.'
    },
    {
      title: 'Mandal General Secretary & Joint Secretary',
      level: 'Mandal',
      responsibilities: [
        'Maintain local records, membership, grievances; convene meetings; monthly reports to District GS.',
        'Draft updates on grassroots initiatives.'
      ],
      accountability: 'Reports to Mandal President/District GS and executive committees.'
    },
    {
      title: 'Mandal Organizing Secretary',
      level: 'Mandal',
      responsibilities: [
        'Drive membership/mobilization; coordinate volunteers; execute campaigns.'
      ],
      accountability: 'Reports to District Organizing Secretary / Mandal President and executive committees.'
    },
    {
      title: 'Mandal Coordinator',
      level: 'Mandal',
      responsibilities: [
        'Monitor local trends/needs; advocate issues; report upward.'
      ],
      accountability: 'Reports to District Coordinators and executive committees.'
    },
    {
      title: 'Mandal Spokesperson',
      level: 'Mandal',
      responsibilities: [
        'Represent AISU in local forums/media; deliver authorized statements.'
      ],
      accountability: 'Reports to District Spokesperson and executive committees.'
    },
    {
      title: 'College Head',
      level: 'College',
      responsibilities: [
        'Lead AISU at institution; membership drives, grievance sessions, events; report concerns to Mandal President.'
      ],
      accountability: 'Reports to Mandal President and District GS/executive committees.'
    },
    {
      title: 'College Ambassador',
      level: 'College',
      responsibilities: [
        'Facilitate AISU-institution communication; promote programs among students.'
      ],
      accountability: 'Reports to College Head and executive committees.'
    },
    {
      title: 'College Member',
      level: 'College',
      responsibilities: [
        'Participate in AISU events; provide feedback; meet membership criteria.'
      ],
      accountability: 'Reports to College Ambassador and executive committees.'
    }
  ];

  useEffect(() => {
    fetchDesignations();
  }, []);

  const fetchDesignations = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch('/accounts/designations/', { headers });

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
      <SimplePage title="Designations" subtitle="Organizational hierarchy">
        <div className="designations-container">
          <div className="loading">Loading designations...</div>
        </div>
      </SimplePage>
    );
  }

  return (
    <SimplePage title="Designations" subtitle="Organizational hierarchy">
      <div className="designations-container">
        <h1 className="designations-title">Organizational Designations</h1>

        {error && (
          <div className="error-message" style={{ marginBottom: '12px' }}>
            Could not load live designations ({error}). Showing DRAR reference data below.
          </div>
        )}

        <div className="designation-level-section drar-block">
          <div className="level-header">
            <h2>Designations by Level (DRAR)</h2>
            <span className="expand-icon expanded">▼</span>
          </div>
          <div className="designation-cards">
            {LEVEL_ORDER.map((level) => (
              <div key={`dras-${level}`} className="designation-card">
                <div className="designation-card-header">
                  <h3>{LEVEL_LABELS[level]} Level</h3>
                </div>
                <ul className="drar-list">
                  {DRAR_LEVELS[level].map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      
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

      <div className="designation-level-section drar-block">
        <div className="level-header">
          <h2>Roles, Authorities & Responsibilities (DRAR)</h2>
          <span className="expand-icon expanded">▼</span>
        </div>
        <div className="designation-cards drar-details">
          {DRAR_DETAILS.map((item) => (
            <div key={item.title} className="designation-card">
              <div className="designation-card-header">
                <div>
                  <h3>{item.title}</h3>
                  <span className="level-badge small">{item.level}</span>
                </div>
              </div>
              <div className="drar-detail-body">
                <ul>
                  {item.responsibilities.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
                {item.authority && (
                  <p><strong>Authority:</strong> {item.authority}</p>
                )}
                {item.accountability && (
                  <p><strong>Accountability:</strong> {item.accountability}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      </div>
    </SimplePage>
  );
}

export default DesignationsList;
