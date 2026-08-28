import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  GitFork, 
  HelpCircle, 
  ShieldAlert, 
  AlertTriangle, 
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

const RiskPaths = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [paths, setPaths] = useState([]);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [loadingPaths, setLoadingPaths] = useState(false);
  const [explainingPathIndex, setExplainingPathIndex] = useState(null);
  const [explanations, setExplanations] = useState({});
  const [error, setError] = useState(null);

  // Fetch agents on mount
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
        setError('Failed to fetch agents list.');
      } finally {
        setLoadingAgents(false);
      }
    };
    fetchAgents();
  }, []);

  // Fetch paths when agent selection changes
  useEffect(() => {
    if (!selectedAgentId) return;

    const fetchPaths = async () => {
      try {
        setLoadingPaths(true);
        const data = await api.getRiskPaths(selectedAgentId);
        setPaths(data);
        setExplanations({}); // Clear previous explanations
      } catch (err) {
        console.error(err);
        setError('Failed to load risk paths for the selected agent.');
      } finally {
        setLoadingPaths(false);
      }
    };
    fetchPaths();
  }, [selectedAgentId]);

  const handleExplain = async (index, path) => {
    try {
      setExplainingPathIndex(index);
      
      // Look up if there's an associated policy in the parent agent details or just construct standard request
      // We'll load the full agent details to see if there are governing policies
      const agentDetails = await api.getAgentDetails(selectedAgentId);
      const policyDetails = agentDetails.policies.length > 0 ? agentDetails.policies[0] : null;
      const riskScoreVal = agentDetails.risk_score ? agentDetails.risk_score.score : 50;

      const res = await api.explainRisk(path.nodes, policyDetails, riskScoreVal);
      
      setExplanations(prev => ({
        ...prev,
        [index]: res.explanation
      }));
    } catch (err) {
      console.error(err);
      setExplanations(prev => ({
        ...prev,
        [index]: 'Failed to generate explanation. Verify connection parameters.'
      }));
    } finally {
      setExplainingPathIndex(null);
    }
  };

  if (loadingAgents) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading agent registry...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>
        <GitFork size={28} color="var(--color-primary)" />
        Risk Path Explorer
      </h1>
      <p className="subtitle">
        Traces multi-hop traversal paths from an AI agent to sensitive or high-risk data sources.
      </p>

      {/* Select Agent Dropdown */}
      <div className="card" style={{ padding: '1rem' }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Select Agent to Analyze:</label>
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

      {loadingPaths && (
        <div className="loading-container" style={{ minHeight: '200px' }}>
          <div className="spinner"></div>
          <p>Auditing graph database for indirect path connections...</p>
        </div>
      )}

      {!loadingPaths && (
        <div>
          {paths.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {paths.map((path, idx) => {
                const targetNode = path.nodes[path.nodes.length - 1];
                const isHighlySensitive = targetNode?.sensitivity === 'Highly Sensitive' || targetNode?.sensitivity === 'Restricted';
                
                return (
                  <div key={idx} className={`card ${isHighlySensitive ? 'critical' : 'medium'}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                      <span className="badge medium">Path Type: {path.path_type} traversal</span>
                      <span className={`badge ${isHighlySensitive ? 'critical' : 'medium'}`}>
                        Target: {targetNode?.sensitivity || 'Public'}
                      </span>
                    </div>

                    {/* Path Chain Visualizer */}
                    <div className="path-viewer">
                      {path.nodes.map((node, nIdx) => (
                        <React.Fragment key={node.id}>
                          <div className={`path-step-node ${node.label}`}>
                            <strong style={{ fontSize: '0.875rem' }}>{node.name}</strong>
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                              {node.label}
                            </span>
                          </div>
                          {nIdx < path.nodes.length - 1 && (
                            <div className="path-arrow">
                              <ArrowRight size={14} />
                            </div>
                          )}
                        </React.Fragment>
                      ))}
                    </div>

                    {/* Explanations & Action Button */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {explanations[idx] ? (
                        <div className="explanation-block">
                          <div className="explanation-title">
                            <ShieldAlert size={14} />
                            Risk Explanation
                          </div>
                          <div className="explanation-text">
                            {explanations[idx]}
                          </div>
                        </div>
                      ) : (
                        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                          <button 
                            className="btn btn-primary"
                            disabled={explainingPathIndex === idx}
                            onClick={() => handleExplain(idx, path)}
                          >
                            {explainingPathIndex === idx ? (
                              <>
                                <div className="spinner" style={{ width: '14px', height: '14px', margin: 0, borderWidth: '2px' }} />
                                Analysing Path...
                              </>
                            ) : (
                              <>
                                <HelpCircle size={16} />
                                Explain This Risk Path
                              </>
                            )}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="empty-container">
              <ShieldCheck size={48} color="var(--risk-low)" />
              <h2>No Risky Paths Found</h2>
              <p style={{ maxWidth: '400px', marginTop: '0.5rem' }}>
                This agent has no execution or permission paths connecting it to Restricted or Highly Sensitive data sources in the current network configuration.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RiskPaths;
