import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  AlertTriangle, 
  ArrowRight, 
  ShieldAlert, 
  ShieldCheck, 
  HelpCircle 
} from 'lucide-react';

const PolicyViolations = () => {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mitigatingIndex, setMitigatingIndex] = useState(null);
  const [error, setError] = useState(null);

  const fetchViolations = async () => {
    try {
      setLoading(true);
      const data = await api.getPolicyViolations();
      setViolations(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch active policy violations from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchViolations();
  }, []);

  const handleMitigate = (index) => {
    setMitigatingIndex(index);
    setTimeout(() => {
      setMitigatingIndex(null);
      alert('Remediation Recommendation:\n1. Revoke the USES relationship between the offending Agent and Tool.\n2. Configure firewall rules on the target Database to reject direct API connections.\n3. Audit governing policies to tighten allowed sensitivities.');
    }, 800);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Scanning graph database for policy violations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <AlertTriangle size={48} color="var(--risk-critical)" />
        <h2 style={{ marginTop: '1rem' }}>Connection Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  const getSeverityBadgeClass = (sev) => {
    switch (sev) {
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
        <AlertTriangle size={28} color="var(--risk-critical)" />
        Policy Violations
      </h1>
      <p className="subtitle">
        Active compliance alerts and data-leak vectors violating governing policies.
      </p>

      {violations.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {violations.map((violation, idx) => {
            const { policy, agent, tool, api: apiNode, datasource, path_type, explanation } = violation;
            
            return (
              <div key={idx} className="card critical">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <div>
                    <h2 style={{ margin: 0, fontSize: '1.1rem' }}>{policy.name}</h2>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Severity: <span className={getSeverityBadgeClass(policy.severity)}>{policy.severity}</span></p>
                  </div>
                  <span className="badge critical">Policy Mismatch</span>
                </div>
                
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  <strong>Policy Description:</strong> {policy.description}
                </p>

                {/* Path display */}
                <div className="path-viewer" style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                  <div className="path-step-node Agent">
                    <strong>{agent.name}</strong>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>AGENT</span>
                  </div>
                  
                  {path_type === 'execution' && tool && apiNode ? (
                    <>
                      <div className="path-arrow"><ArrowRight size={12} /></div>
                      <div className="path-step-node Tool">
                        <strong>{tool.name}</strong>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>TOOL</span>
                      </div>
                      <div className="path-arrow"><ArrowRight size={12} /></div>
                      <div className="path-step-node API">
                        <strong>{apiNode.name}</strong>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>API</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="path-arrow"><ArrowRight size={12} /></div>
                      <div className="path-step-node Permission">
                        <strong>Direct Permissions</strong>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PERMISSION</span>
                      </div>
                    </>
                  )}
                  
                  <div className="path-arrow"><ArrowRight size={12} /></div>
                  <div className="path-step-node DataSource">
                    <strong>{datasource.name}</strong>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DATASOURCE ({datasource.sensitivity})</span>
                  </div>
                </div>

                {/* Explanation block */}
                <div className="explanation-block" style={{ marginTop: 0 }}>
                  <div className="explanation-title">
                    <ShieldAlert size={14} color="var(--risk-critical)" />
                    Compliance Violations Alert
                  </div>
                  <div className="explanation-text" style={{ fontSize: '0.875rem' }}>
                    {explanation}
                  </div>
                </div>

                {/* Mitigate actions button */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <button 
                    className="btn btn-primary"
                    disabled={mitigatingIndex === idx}
                    onClick={() => handleMitigate(idx)}
                    style={{ backgroundColor: 'var(--risk-critical)', borderColor: 'var(--risk-critical)', color: '#fff' }}
                  >
                    {mitigatingIndex === idx ? (
                      <>
                        <div className="spinner" style={{ width: '14px', height: '14px', margin: 0, borderWidth: '2px', borderLeftColor: '#fff' }} />
                        Loading Recommendation...
                      </>
                    ) : (
                      'Review Remediation'
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="empty-container">
          <ShieldCheck size={48} color="var(--risk-low)" />
          <h2>All Clear: No Violations Detected</h2>
          <p style={{ maxWidth: '400px', marginTop: '0.5rem' }}>
            All active agent database traversals comply with company security policies.
          </p>
        </div>
      )}
    </div>
  );
};

export default PolicyViolations;
