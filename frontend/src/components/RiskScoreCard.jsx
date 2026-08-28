import React from 'react';

const RiskScoreCard = ({ riskScore }) => {
  if (!riskScore) return null;
  const { score, level, factors, breakdown } = riskScore;

  const getRiskClass = (lvl) => {
    switch (lvl) {
      case 'Critical': return 'critical';
      case 'High': return 'high';
      case 'Medium': return 'medium';
      case 'Low': return 'low';
      default: return 'low';
    }
  };

  return (
    <div className={`card ${getRiskClass(level)}`}>
      <h2>Security Risk Analysis</h2>
      <div className="risk-meter-container" style={{ marginTop: '1rem' }}>
        <div className={`risk-circle ${getRiskClass(level)}`} style={{ border: '4px solid var(--border-color)', backgroundColor: 'var(--bg-input)' }}>
          <span className="score" style={{ color: `var(--risk-${level.toLowerCase()})` }}>{score}</span>
          <span className="max">Risk Score</span>
        </div>
        
        <div className="risk-factors-list">
          <div className="risk-factor-row">
            <span>Data Sensitivity (Max 30)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="risk-factor-bar-bg">
                <div className="risk-factor-bar" style={{ width: `${(factors.data_sensitivity / 30) * 100}%`, backgroundColor: 'var(--color-datasource)' }}></div>
              </div>
              <span style={{ minWidth: '20px', textAlign: 'right' }}>{factors.data_sensitivity}</span>
            </div>
          </div>

          <div className="risk-factor-row">
            <span>Tool Risk (Max 25)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="risk-factor-bar-bg">
                <div className="risk-factor-bar" style={{ width: `${(factors.tool_risk / 25) * 100}%`, backgroundColor: 'var(--color-tool)' }}></div>
              </div>
              <span style={{ minWidth: '20px', textAlign: 'right' }}>{factors.tool_risk}</span>
            </div>
          </div>

          <div className="risk-factor-row">
            <span>Blast Radius Impact (Max 15)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="risk-factor-bar-bg">
                <div className="risk-factor-bar" style={{ width: `${(factors.blast_radius / 15) * 100}%`, backgroundColor: 'var(--color-api)' }}></div>
              </div>
              <span style={{ minWidth: '20px', textAlign: 'right' }}>{factors.blast_radius}</span>
            </div>
          </div>

          <div className="risk-factor-row">
            <span>Policy Violations (Max 20)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="risk-factor-bar-bg">
                <div className="risk-factor-bar" style={{ width: `${(factors.policy_violations / 20) * 100}%`, backgroundColor: 'var(--color-policy)' }}></div>
              </div>
              <span style={{ minWidth: '20px', textAlign: 'right' }}>{factors.policy_violations}</span>
            </div>
          </div>

          <div className="risk-factor-row">
            <span>Exposed Secrets (Max 10)</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="risk-factor-bar-bg">
                <div className="risk-factor-bar" style={{ width: `${(factors.exposed_secrets / 10) * 100}%`, backgroundColor: 'var(--color-secret)' }}></div>
              </div>
              <span style={{ minWidth: '20px', textAlign: 'right' }}>{factors.exposed_secrets}</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.8125rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', color: 'var(--text-secondary)' }}>
        <div>
          <p>Risk Band: <span className={`badge ${getRiskClass(level)}`}>{level} Risk</span></p>
          <p style={{ marginTop: '0.5rem' }}>Max Reachable Sensitivity: <strong style={{ color: 'var(--text-primary)' }}>{breakdown.max_sensitivity}</strong></p>
          <p style={{ marginTop: '0.25rem' }}>Max Tool Risk: <strong style={{ color: 'var(--text-primary)' }}>{breakdown.max_tool_risk}</strong></p>
        </div>
        <div>
          <p>Reachable DataSources: <strong style={{ color: 'var(--text-primary)' }}>{breakdown.reachable_datasources_count}</strong></p>
          <p style={{ marginTop: '0.25rem' }}>Reachable APIs: <strong style={{ color: 'var(--text-primary)' }}>{breakdown.reachable_apis_count}</strong></p>
          <p style={{ marginTop: '0.25rem' }}>Active Violations: <strong style={{ color: 'var(--text-primary)' }}>{breakdown.policy_violations_count}</strong></p>
        </div>
      </div>
    </div>
  );
};

export default RiskScoreCard;
