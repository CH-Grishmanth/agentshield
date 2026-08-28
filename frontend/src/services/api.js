const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
const HEALTH_URL = API_BASE.endsWith('/api') ? API_BASE.slice(0, -4) + '/health' : API_BASE + '/health';

export const api = {
  getHealth: async () => {
    const res = await fetch(HEALTH_URL);
    return res.json();
  },
  getDashboardStats: async () => {
    const res = await fetch(`${API_BASE}/dashboard`);
    if (!res.ok) throw new Error('Failed to fetch dashboard stats');
    return res.json();
  },
  getAgents: async () => {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agents list');
    return res.json();
  },
  getAgentDetails: async (id) => {
    const res = await fetch(`${API_BASE}/agents/${id}`);
    if (!res.ok) throw new Error('Failed to fetch agent details');
    return res.json();
  },
  getReachableResources: async (id) => {
    const res = await fetch(`${API_BASE}/agents/${id}/reachable-resources`);
    if (!res.ok) throw new Error('Failed to fetch reachable resources');
    return res.json();
  },
  getRiskPaths: async (id) => {
    const res = await fetch(`${API_BASE}/agents/${id}/risk-paths`);
    if (!res.ok) throw new Error('Failed to fetch risk paths');
    return res.json();
  },
  getToolBlastRadius: async (id) => {
    const res = await fetch(`${API_BASE}/tools/${id}/blast-radius`);
    if (!res.ok) throw new Error('Failed to fetch tool blast radius');
    return res.json();
  },
  getAgentBlastRadius: async (id) => {
    const res = await fetch(`${API_BASE}/agents/${id}/blast-radius`);
    if (!res.ok) throw new Error('Failed to fetch agent blast radius');
    return res.json();
  },
  getPolicyViolations: async () => {
    const res = await fetch(`${API_BASE}/policies/violations`);
    if (!res.ok) throw new Error('Failed to fetch policy violations');
    return res.json();
  },
  getGraphData: async () => {
    const res = await fetch(`${API_BASE}/graph`);
    if (!res.ok) throw new Error('Failed to fetch graph data');
    return res.json();
  },
  getTools: async () => {
    const res = await fetch(`${API_BASE}/tools`);
    if (!res.ok) throw new Error('Failed to fetch tools list');
    return res.json();
  },
  explainRisk: async (pathNodes, policyDetails, riskScore) => {
    const res = await fetch(`${API_BASE}/agents/explain-risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path_nodes: pathNodes,
        policy_details: policyDetails,
        risk_score: riskScore
      })
    });
    if (!res.ok) throw new Error('Failed to generate risk explanation');
    return res.json();
  }
};
