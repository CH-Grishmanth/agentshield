import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  UserCheck, 
  Settings, 
  Globe, 
  Database, 
  FileText, 
  Key, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle,
  TrendingUp
} from 'lucide-react';

const Dashboard = ({ setCurrentPage }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await api.getDashboardStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('Failed to connect to the AgentShield backend server. Please verify the backend is running and CognoDB connection is active.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading AgentShield metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <AlertTriangle size={48} color="var(--risk-critical)" />
        <h2 style={{ marginTop: '1rem' }}>Database / API Connection Error</h2>
        <p style={{ maxWidth: '500px', margin: '0.5rem auto 1.5rem auto' }}>{error}</p>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>
          Retry Connection
        </button>
      </div>
    );
  }

  const { agents, tools, apis, datasources, policies, secrets, risk_distribution } = stats;

  const totalRisky = (risk_distribution.Critical || 0) + (risk_distribution.High || 0);

  return (
    <div>
      <h1>
        <ShieldAlert size={28} color="var(--color-primary)" />
        AgentShield Dashboard
      </h1>
      <p className="subtitle">
        Explainable security graph audit log for AI agents, tools, APIs, permissions and data sources.
      </p>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-agent)' }}>
            <UserCheck size={20} />
          </div>
          <div>
            <div className="value">{agents}</div>
            <div className="label">Agents</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-tool)' }}>
            <Settings size={20} />
          </div>
          <div>
            <div className="value">{tools}</div>
            <div className="label">Tools</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-api)' }}>
            <Globe size={20} />
          </div>
          <div>
            <div className="value">{apis}</div>
            <div className="label">APIs</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-datasource)' }}>
            <Database size={20} />
          </div>
          <div>
            <div className="value">{datasources}</div>
            <div className="label">Data Sources</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-policy)' }}>
            <FileText size={20} />
          </div>
          <div>
            <div className="value">{policies}</div>
            <div className="label">Policies</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="icon-wrapper" style={{ color: 'var(--color-secret)' }}>
            <Key size={20} />
          </div>
          <div>
            <div className="value">{secrets}</div>
            <div className="label">Secrets</div>
          </div>
        </div>
      </div>

      <div className="grid-2col">
        {/* Risk Distribution Summary */}
        <div className="card">
          <h2>Security Risk Status</h2>
          <p style={{ fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Calculated risk score distributions across active AI agents.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                <span className="badge critical">Critical Risk</span>
                <span style={{ fontWeight: '600' }}>{risk_distribution.Critical || 0}</span>
              </div>
              <div className="risk-factor-bar-bg" style={{ width: '100%' }}>
                <div className="risk-factor-bar" style={{ width: `${((risk_distribution.Critical || 0) / (agents || 1)) * 100}%`, backgroundColor: 'var(--risk-critical)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                <span className="badge high">High Risk</span>
                <span style={{ fontWeight: '600' }}>{risk_distribution.High || 0}</span>
              </div>
              <div className="risk-factor-bar-bg" style={{ width: '100%' }}>
                <div className="risk-factor-bar" style={{ width: `${((risk_distribution.High || 0) / (agents || 1)) * 100}%`, backgroundColor: 'var(--risk-high)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                <span className="badge medium">Medium Risk</span>
                <span style={{ fontWeight: '600' }}>{risk_distribution.Medium || 0}</span>
              </div>
              <div className="risk-factor-bar-bg" style={{ width: '100%' }}>
                <div className="risk-factor-bar" style={{ width: `${((risk_distribution.Medium || 0) / (agents || 1)) * 100}%`, backgroundColor: 'var(--risk-medium)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                <span className="badge low">Low Risk</span>
                <span style={{ fontWeight: '600' }}>{risk_distribution.Low || 0}</span>
              </div>
              <div className="risk-factor-bar-bg" style={{ width: '100%' }}>
                <div className="risk-factor-bar" style={{ width: `${((risk_distribution.Low || 0) / (agents || 1)) * 100}%`, backgroundColor: 'var(--risk-low)' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Action Center */}
        <div className="card">
          <h2>Security Action Center</h2>
          <p style={{ fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Core security tasks that need immediate inspection in the system.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {totalRisky > 0 ? (
              <div className="explanation-block" style={{ borderLeft: '4px solid var(--risk-critical)', display: 'flex', alignItems: 'flex-start', gap: '0.75rem', backgroundColor: 'rgba(255,62,62,0.03)' }}>
                <AlertTriangle color="var(--risk-critical)" size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <h3 style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Risky Agents Detected</h3>
                  <p style={{ fontSize: '0.8125rem', marginTop: '0.25rem' }}>
                    There are {totalRisky} agents classified under Critical or High Risk levels. Examine their reachable paths to block unsafe queries.
                  </p>
                  <button 
                    className="btn btn-primary" 
                    style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem', marginTop: '0.5rem' }}
                    onClick={() => setCurrentPage('agents')}
                  >
                    Investigate Agents
                  </button>
                </div>
              </div>
            ) : (
              <div className="explanation-block" style={{ borderLeft: '4px solid var(--risk-low)', display: 'flex', alignItems: 'flex-start', gap: '0.75rem', backgroundColor: 'rgba(0,230,118,0.03)' }}>
                <CheckCircle color="var(--risk-low)" size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <h3 style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Systems Secured</h3>
                  <p style={{ fontSize: '0.8125rem', marginTop: '0.25rem' }}>
                    No critical vulnerabilities are currently flagged in agent configuration parameters.
                  </p>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <button 
                className="btn btn-secondary" 
                style={{ flex: 1, fontSize: '0.8125rem' }} 
                onClick={() => setCurrentPage('violations')}
              >
                View Policy Violations
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ flex: 1, fontSize: '0.8125rem' }} 
                onClick={() => setCurrentPage('paths')}
              >
                Inspect Risk Paths
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
