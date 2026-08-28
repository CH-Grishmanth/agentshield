import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import RiskScoreCard from '../components/RiskScoreCard';
import { 
  UserCheck, 
  Settings, 
  Globe, 
  Database, 
  FileText, 
  Key, 
  ShieldAlert, 
  AlertTriangle 
} from 'lucide-react';

const AgentExplorer = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [agentDetails, setAgentDetails] = useState(null);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState(null);

  // Fetch agents list on mount
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoadingAgents(true);
        const data = await api.getAgents();
        setAgents(data);
        if (data.length > 0) {
          setSelectedAgentId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to fetch agents. Ensure backend is running.');
      } finally {
        setLoadingAgents(false);
      }
    };
    fetchAgents();
  }, []);

  // Fetch agent details when selectedAgentId changes
  useEffect(() => {
    if (!selectedAgentId) return;

    const fetchDetails = async () => {
      try {
        setLoadingDetails(true);
        const data = await api.getAgentDetails(selectedAgentId);
        setAgentDetails(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load agent details.');
      } finally {
        setLoadingDetails(false);
      }
    };
    fetchDetails();
  }, [selectedAgentId]);

  if (loadingAgents) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading agent registry...</p>
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

  return (
    <div>
      <h1>
        <UserCheck size={28} color="var(--color-primary)" />
        Agent Explorer
      </h1>
      <p className="subtitle">
        Inspect an AI Agent's active tools, permissions, governing policies, secrets, and calculated risk score.
      </p>

      {/* Select Agent Dropdown */}
      <div className="card" style={{ padding: '1rem' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Select Agent to Inspect:</label>
          <select 
            value={selectedAgentId} 
            onChange={(e) => setSelectedAgentId(e.target.value)}
          >
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingDetails && (
        <div className="loading-container" style={{ minHeight: '200px' }}>
          <div className="spinner"></div>
          <p>Analyzing agent security parameters...</p>
        </div>
      )}

      {!loadingDetails && agentDetails && (
        <div className="grid-2col">
          {/* Left Column: Details & Assets */}
          <div>
            {/* General Info */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ marginBottom: '0.25rem' }}>{agentDetails.agent.name}</h2>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>ID: {agentDetails.agent.id} | Category: {agentDetails.agent.category}</p>
                </div>
                <span className={getRiskBadgeClass(agentDetails.agent.risk_level)}>{agentDetails.agent.risk_level} Base Risk</span>
              </div>
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {agentDetails.agent.description}
              </p>
            </div>

            {/* Tools Used */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Settings size={18} color="var(--color-tool)" />
                <h3 style={{ margin: 0 }}>Active Tools Used ({agentDetails.tools.length})</h3>
              </div>
              {agentDetails.tools.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {agentDetails.tools.map((tool) => (
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
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>This agent does not use any tools.</p>
              )}
            </div>

            {/* Secrets Held */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Key size={18} color="var(--color-secret)" />
                <h3 style={{ margin: 0 }}>Credentials / Secrets Exposed ({agentDetails.secrets.length})</h3>
              </div>
              {agentDetails.secrets.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {agentDetails.secrets.map((secret) => (
                    <div key={secret.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                      <div>
                        <strong>{secret.name}</strong>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Type: {secret.type}</p>
                      </div>
                      <span className={getRiskBadgeClass(secret.exposure_level)}>{secret.exposure_level} Exposure</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>This agent has no secrets attached directly.</p>
              )}
            </div>
          </div>

          {/* Right Column: Risk Analysis & Policies */}
          <div>
            {/* Risk Card */}
            <RiskScoreCard riskScore={agentDetails.risk_score} />

            {/* Governing Policies */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <FileText size={18} color="var(--color-policy)" />
                <h3 style={{ margin: 0 }}>Governing Policies ({agentDetails.policies.length})</h3>
              </div>
              {agentDetails.policies.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {agentDetails.policies.map((policy) => (
                    <div key={policy.id} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <strong>{policy.name}</strong>
                        <span className={getRiskBadgeClass(policy.severity)}>{policy.severity}</span>
                      </div>
                      <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>{policy.description}</p>
                      {policy.forbidden_categories && policy.forbidden_categories.length > 0 && (
                        <p style={{ fontSize: '0.75rem', color: 'var(--risk-high)', marginTop: '0.5rem' }}>
                          Forbidden Categories: {policy.forbidden_categories.join(', ')}
                        </p>
                      )}
                      {policy.forbidden_sensitivities && policy.forbidden_sensitivities.length > 0 && (
                        <p style={{ fontSize: '0.75rem', color: 'var(--risk-critical)', marginTop: '0.25rem' }}>
                          Forbidden Sensitivities: {policy.forbidden_sensitivities.join(', ')}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>This agent has no governing policy restrictions.</p>
              )}
            </div>

            {/* Direct Permissions */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <ShieldAlert size={18} color="var(--color-permission)" />
                <h3 style={{ margin: 0 }}>Direct Permissions ({agentDetails.permissions.length})</h3>
              </div>
              {agentDetails.permissions.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {agentDetails.permissions.map((perm) => (
                    <div key={perm.id} style={{ display: 'flex', justifySelf: 'stretch', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                      <div>
                        <strong>{perm.name}</strong>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Scope: {perm.scope}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>This agent has no direct permissions.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentExplorer;
