import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Activity, 
  Settings, 
  UserCheck, 
  Globe, 
  Database, 
  Key, 
  AlertTriangle,
  AlertOctagon
} from 'lucide-react';

const BlastRadius = () => {
  const [targetType, setTargetType] = useState('tool'); // 'tool' or 'agent'
  const [list, setList] = useState([]); // tools or agents
  const [selectedId, setSelectedId] = useState('');
  const [blastData, setBlastData] = useState(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingBlast, setLoadingBlast] = useState(false);
  const [error, setError] = useState(null);

  // Fetch tools or agents list based on targetType
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoadingList(true);
        setBlastData(null);
        setSelectedId('');
        if (targetType === 'tool') {
          const data = await api.getTools();
          setList(data);
          if (data.length > 0) setSelectedId(data[0].id);
        } else {
          const data = await api.getAgents();
          setList(data);
          if (data.length > 0) setSelectedId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to fetch node registry.');
      } finally {
        setLoadingList(false);
      }
    };
    fetchData();
  }, [targetType]);

  // Fetch blast radius when selectedId changes
  useEffect(() => {
    if (!selectedId) return;

    const fetchBlastRadius = async () => {
      try {
        setLoadingBlast(true);
        if (targetType === 'tool') {
          const data = await api.getToolBlastRadius(selectedId);
          setBlastData(data);
        } else {
          const data = await api.getAgentBlastRadius(selectedId);
          setBlastData(data);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to compute blast radius.');
      } finally {
        setLoadingBlast(false);
      }
    };
    fetchBlastRadius();
  }, [selectedId, targetType]);

  if (loadingList) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading asset directories...</p>
      </div>
    );
  }

  const getRiskBadgeClass = (lvl) => {
    switch (lvl) {
      case 'Critical': return 'badge critical';
      case 'High': return 'badge high';
      case 'Medium': return 'badge medium';
      case 'Low': return 'badge low';
      default: return 'badge low';
    }
  };

  const getSensitivityClass = (sens) => {
    if (sens === 'Highly Sensitive' || sens === 'Restricted') return 'critical';
    if (sens === 'Confidential') return 'medium';
    return 'low';
  };

  return (
    <div>
      <h1>
        <Activity size={28} color="var(--color-primary)" />
        Blast Radius Analyzer
      </h1>
      <p className="subtitle">
        Evaluate the security blast radius and compromised assets if an agent or tool credentials are leaked.
      </p>

      {/* Target selector type and dropdown */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div className="grid-2col" style={{ gap: '1rem', alignItems: 'center' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Compromise Target Type:</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.875rem' }}>
                <input 
                  type="radio" 
                  name="targetType" 
                  value="tool" 
                  checked={targetType === 'tool'} 
                  onChange={() => setTargetType('tool')} 
                  style={{ width: 'auto', cursor: 'pointer' }}
                />
                Tool Compromise
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.875rem' }}>
                <input 
                  type="radio" 
                  name="targetType" 
                  value="agent" 
                  checked={targetType === 'agent'} 
                  onChange={() => setTargetType('agent')} 
                  style={{ width: 'auto', cursor: 'pointer' }}
                />
                Agent Leak
              </label>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Select Asset under Threat:</label>
            <select 
              value={selectedId} 
              onChange={(e) => setSelectedId(e.target.value)}
            >
              {list.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({item.category})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loadingBlast && (
        <div className="loading-container" style={{ minHeight: '200px' }}>
          <div className="spinner"></div>
          <p>Traversing graph relationships downstream to evaluate blast radius...</p>
        </div>
      )}

      {!loadingBlast && blastData && ((targetType === 'tool' && blastData.tool) || (targetType === 'agent' && blastData.agent)) && (
        <div>
          {/* Summary Warning */}
          <div className="explanation-block" style={{ borderLeft: '4px solid var(--risk-critical)', display: 'flex', gap: '0.75rem', backgroundColor: 'rgba(255,62,62,0.03)', marginBottom: '1.5rem' }}>
            <AlertOctagon size={24} color="var(--risk-critical)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h3 style={{ color: 'var(--text-primary)', fontSize: '1rem' }}>Compromise Impact Summary</h3>
              <p style={{ marginTop: '0.25rem', fontSize: '0.875rem' }}>
                {targetType === 'tool' ? (
                  <>
                    If the tool <strong>{blastData.tool.name}</strong> is compromised, it immediately impacts 
                    {' '}<strong>{blastData.affected_agents.length}</strong> agents relying on it, calls 
                    {' '}<strong>{blastData.affected_apis.length}</strong> APIs and exposes 
                    {' '}<strong>{blastData.affected_datasources.length}</strong> downstream data sources.
                  </>
                ) : (
                  <>
                    If the agent credentials for <strong>{blastData.agent.name}</strong> are leaked, it immediately exposes 
                    {' '}<strong>{blastData.affected_tools.length}</strong> tools, 
                    {' '}<strong>{blastData.affected_apis.length}</strong> APIs, 
                    {' '}<strong>{blastData.affected_secrets.length}</strong> credentials, and 
                    {' '}<strong>{blastData.affected_datasources.length}</strong> data sources.
                  </>
                )}
              </p>
            </div>
          </div>

          <div className="grid-2col">
            {/* Left Column: Affected Agents / Tools */}
            <div className="card">
              {targetType === 'tool' ? (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <UserCheck size={18} color="var(--color-agent)" />
                    <h3 style={{ margin: 0 }}>Affected AI Agents ({blastData.affected_agents.length})</h3>
                  </div>
                  {blastData.affected_agents.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {blastData.affected_agents.map((agent) => (
                        <div key={agent.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                          <div>
                            <strong>{agent.name}</strong>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Category: {agent.category}</p>
                          </div>
                          <span className={getRiskBadgeClass(agent.risk_level)}>{agent.risk_level}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No agents use this tool.</p>
                  )}
                </>
              ) : (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <Settings size={18} color="var(--color-tool)" />
                    <h3 style={{ margin: 0 }}>Affected Tools ({blastData.affected_tools.length})</h3>
                  </div>
                  {blastData.affected_tools.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {blastData.affected_tools.map((tool) => (
                        <div key={tool.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                          <div>
                            <strong>{tool.name}</strong>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{tool.description}</p>
                          </div>
                          <span className={getRiskBadgeClass(tool.risk_level)}>{tool.risk_level}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No tools affected.</p>
                  )}
                </>
              )}
            </div>

            {/* Right Column: Affected Data Sources */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Database size={18} color="var(--color-datasource)" />
                <h3 style={{ margin: 0 }}>Exposed Data Sources ({blastData.affected_datasources.length})</h3>
              </div>
              {blastData.affected_datasources.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {blastData.affected_datasources.map((ds) => {
                    const isSens = ds.sensitivity === 'Highly Sensitive' || ds.sensitivity === 'Restricted';
                    return (
                      <div key={ds.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                        <div>
                          <strong>{ds.name}</strong>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Category: {ds.category}</p>
                        </div>
                        <span className={`badge ${getSensitivityClass(ds.sensitivity)}`}>{ds.sensitivity}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No downstream data sources exposed.</p>
              )}
            </div>
          </div>

          <div className="grid-2col" style={{ marginTop: '1.5rem' }}>
            {/* Affected APIs */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Globe size={18} color="var(--color-api)" />
                <h3 style={{ margin: 0 }}>Exposed API Integrations ({blastData.affected_apis.length})</h3>
              </div>
              {blastData.affected_apis.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {blastData.affected_apis.map((api) => (
                    <div key={api.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                      <div>
                        <strong>{api.name}</strong>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Endpoint: {api.endpoint}</p>
                      </div>
                      <span className={getRiskBadgeClass(api.risk_level)}>{api.risk_level}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No API integrations exposed.</p>
              )}
            </div>

            {/* Affected Secrets (if agent) */}
            {targetType === 'agent' && (
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <Key size={18} color="var(--color-secret)" />
                  <h3 style={{ margin: 0 }}>Exposed Credentials ({blastData.affected_secrets.length})</h3>
                </div>
                {blastData.affected_secrets.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {blastData.affected_secrets.map((secret) => (
                      <div key={secret.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                        <div>
                          <strong>{secret.name}</strong>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Type: {secret.type}</p>
                        </div>
                        <span className={getRiskBadgeClass(secret.exposure_level)}>{secret.exposure_level}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No credentials leaked directly.</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BlastRadius;
