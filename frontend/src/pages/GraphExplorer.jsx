import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import NetworkGraph from '../components/NetworkGraph';
import { 
  Search, 
  Database, 
  ShieldAlert, 
  Settings, 
  Globe, 
  Key, 
  Info,
  Filter
} from 'lucide-react';

const GraphExplorer = () => {
  const [graphData, setGraphData] = useState(null);
  const [filteredGraphData, setFilteredGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtering checkboxes state
  const [filters, setFilters] = useState({
    Agent: true,
    Tool: true,
    API: true,
    DataSource: true,
    Policy: true,
    Secret: true,
    Permission: true
  });

  // Fetch full graph on mount
  useEffect(() => {
    const fetchGraph = async () => {
      try {
        setLoading(true);
        const data = await api.getGraphData();
        setGraphData(data);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('Failed to load complete graph data.');
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, []);

  // Update filtered graph data whenever raw data or filters change
  useEffect(() => {
    if (!graphData) return;

    // Filter nodes
    const filteredNodes = graphData.nodes.filter(node => filters[node.label]);
    
    // Filter edges: only keep edges where both source and target nodes are currently visible
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = graphData.edges.filter(
      edge => nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );

    setFilteredGraphData({
      nodes: filteredNodes,
      edges: filteredEdges
    });

    // Reset selected node if it is filtered out
    if (selectedNode && !nodeIds.has(selectedNode.id)) {
      setSelectedNode(null);
    }
  }, [graphData, filters]);

  const handleFilterToggle = (key) => {
    setFilters(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Rendering interactive security landscape map...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>
        <Search size={28} color="var(--color-primary)" />
        Graph Explorer
      </h1>
      <p className="subtitle">
        Explore relationships in the security network. Toggle filter nodes to isolate specific risk vectors.
      </p>

      {/* Grid containing Filters / Legend & Main Viewport */}
      <div className="grid-2col" style={{ gridTemplateColumns: '1fr 320px', gap: '1.5rem', alignItems: 'stretch' }}>
        {/* Main Canvas Viewport */}
        <div>
          {filteredGraphData && (
            <NetworkGraph 
              data={filteredGraphData} 
              onNodeSelect={setSelectedNode} 
            />
          )}
        </div>

        {/* Filters and Property Inspector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Graph filters */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <Filter size={16} color="var(--color-primary)" />
              <h3 style={{ margin: 0 }}>Filter Nodes</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem', fontSize: '0.875rem' }}>
              {Object.keys(filters).map((type) => (
                <label key={type} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={filters[type]} 
                    onChange={() => handleFilterToggle(type)}
                    style={{ width: 'auto', margin: 0, cursor: 'pointer' }}
                  />
                  {type}
                </label>
              ))}
            </div>
          </div>

          {/* Properties Inspector */}
          <div className="card" style={{ flexGrow: 1, padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              <Info size={16} color="var(--color-primary)" />
              <h3 style={{ margin: 0 }}>Node Inspector</h3>
            </div>

            {selectedNode ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.875rem' }}>
                <div>
                  <label className="form-label">Name</label>
                  <div style={{ fontWeight: '600', fontSize: '1rem' }}>{selectedNode.name}</div>
                </div>

                <div>
                  <label className="form-label">Node Type</label>
                  <div>
                    <span className="badge" style={{ backgroundColor: 'var(--bg-input)', borderColor: 'var(--border-color)', border: '1px solid var(--border-color)', textTransform: 'uppercase' }}>
                      {selectedNode.label}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="form-label">ID</label>
                  <code style={{ fontSize: '0.75rem', backgroundColor: 'var(--bg-input)', padding: '0.2rem 0.4rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}>{selectedNode.id}</code>
                </div>

                {selectedNode.description && (
                  <div>
                    <label className="form-label">Description</label>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>{selectedNode.description}</p>
                  </div>
                )}

                {selectedNode.category && (
                  <div>
                    <label className="form-label">Category</label>
                    <div style={{ color: 'var(--text-primary)' }}>{selectedNode.category}</div>
                  </div>
                )}

                {selectedNode.risk_level && (
                  <div>
                    <label className="form-label">Risk Level</label>
                    <div>
                      <span className={getRiskBadgeClass(selectedNode.risk_level)}>{selectedNode.risk_level}</span>
                    </div>
                  </div>
                )}

                {selectedNode.sensitivity && (
                  <div>
                    <label className="form-label">Sensitivity</label>
                    <div>
                      <span className={`badge ${getSensitivityClass(selectedNode.sensitivity)}`}>{selectedNode.sensitivity}</span>
                    </div>
                  </div>
                )}

                {selectedNode.provider && (
                  <div>
                    <label className="form-label">Provider</label>
                    <div style={{ color: 'var(--text-primary)' }}>{selectedNode.provider}</div>
                  </div>
                )}

                {selectedNode.endpoint && (
                  <div>
                    <label className="form-label">Endpoint</label>
                    <code style={{ fontSize: '0.75rem', display: 'block', wordBreak: 'break-all', backgroundColor: 'var(--bg-input)', padding: '0.4rem', border: '1px solid var(--border-color)', borderRadius: '4px' }}>{selectedNode.endpoint}</code>
                  </div>
                )}

                {selectedNode.type && (
                  <div>
                    <label className="form-label">Secret Type</label>
                    <div style={{ color: 'var(--text-primary)' }}>{selectedNode.type}</div>
                  </div>
                )}

                {selectedNode.exposure_level && (
                  <div>
                    <label className="form-label">Exposure Level</label>
                    <div>
                      <span className={getRiskBadgeClass(selectedNode.exposure_level)}>{selectedNode.exposure_level}</span>
                    </div>
                  </div>
                )}

                {selectedNode.scope && (
                  <div>
                    <label className="form-label">Scope</label>
                    <div style={{ color: 'var(--text-primary)', textTransform: 'uppercase', fontSize: '0.8125rem' }}>{selectedNode.scope}</div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '180px', color: 'var(--text-muted)', textAlign: 'center' }}>
                <Info size={32} style={{ marginBottom: '0.75rem', opacity: 0.5 }} />
                <p style={{ fontSize: '0.8125rem' }}>Click any node on the graph canvas to inspect its security metadata.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphExplorer;
