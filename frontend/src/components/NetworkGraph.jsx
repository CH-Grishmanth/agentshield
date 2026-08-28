import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

const NetworkGraph = ({ data, onNodeSelect }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !data || !data.nodes) return;

    // Map nodes to vis.js format
    const visNodes = data.nodes.map((node) => {
      let color = '#9ca3af';
      let shape = 'dot';
      let fontColor = '#f3f4f6';

      const label = node.label || 'Unknown';
      switch (label) {
        case 'Agent':
          color = '#c084fc';
          shape = 'hexagon';
          break;
        case 'Tool':
          color = '#f472b6';
          shape = 'dot';
          break;
        case 'API':
          color = '#60a5fa';
          shape = 'square';
          break;
        case 'DataSource':
          color = '#34d399';
          shape = 'database';
          break;
        case 'Policy':
          color = '#fb7185';
          shape = 'triangle';
          break;
        case 'Secret':
          color = '#fbbf24';
          shape = 'star';
          break;
        case 'Permission':
          color = '#22d3ee';
          shape = 'diamond';
          break;
        default:
          color = '#9ca3af';
      }

      // Highlight critical and high sensitivity nodes
      const isCritical = node.risk_level === 'Critical' || node.sensitivity === 'Highly Sensitive';
      
      return {
        id: node.id,
        label: `${node.name}\n(${label})`,
        title: node.description || '',
        color: {
          background: color,
          border: isCritical ? '#ff3e3e' : '#242c3d',
          highlight: {
            background: color,
            border: '#00f0ff'
          }
        },
        shape: shape,
        size: label === 'Agent' ? 24 : 16,
        font: {
          color: fontColor,
          size: 10,
          face: 'Inter, sans-serif'
        },
        shadow: {
          enabled: isCritical,
          color: '#ff3e3e',
          size: 10,
          x: 0,
          y: 0
        },
        borderWidth: isCritical ? 3 : 2,
        raw: node
      };
    });

    const visEdges = data.edges.map((edge) => {
      let color = '#242c3d';
      if (edge.type === 'USES') color = '#c084fc';
      else if (edge.type === 'CALLS') color = '#f472b6';
      else if (edge.type === 'ACCESSES') color = '#34d399';
      else if (edge.type === 'GOVERNED_BY') color = '#fb7185';
      else if (edge.type === 'HAS_SECRET') color = '#fbbf24';
      else if (edge.type === 'HAS_PERMISSION') color = '#22d3ee';
      else if (edge.type === 'ALLOWS') color = '#00f0ff';

      return {
        id: edge.id,
        from: edge.source,
        to: edge.target,
        label: edge.type,
        color: {
          color: color,
          highlight: '#00f0ff'
        },
        font: {
          color: '#9ca3af',
          size: 10,
          face: 'JetBrains Mono, Courier New, monospace',
          align: 'middle',
          strokeWidth: 2,
          strokeColor: '#0a0c10'
        },
        arrows: 'to',
        width: 1.5
      };
    });

    const visData = {
      nodes: visNodes,
      edges: visEdges
    };

    const options = {
      physics: {
        stabilization: {
          iterations: 150,
          fit: true
        },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 95,
          springConstant: 0.04
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        selectable: true
      }
    };

    const network = new Network(containerRef.current, visData, options);
    networkRef.current = network;

    // Once layout is stable, freeze physics to keep it from jumping around
    network.on('stabilizationIterationsDone', () => {
      network.setOptions({ physics: false });
    });

    network.on('click', (params) => {
      if (params.nodes && params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const clickedNode = visNodes.find((n) => n.id === nodeId);
        if (clickedNode && onNodeSelect) {
          onNodeSelect(clickedNode.raw);
        }
      }
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [data]);

  return (
    <div className="graph-container">
      <div ref={containerRef} className="graph-canvas" />
      <div className="graph-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-agent)' }} />
          <span>Agent</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-tool)' }} />
          <span>Tool</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-api)' }} />
          <span>API</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-datasource)' }} />
          <span>DataSource</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-permission)' }} />
          <span>Permission</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-secret)' }} />
          <span>Secret</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'var(--color-policy)' }} />
          <span>Policy</span>
        </div>
      </div>
    </div>
  );
};

export default NetworkGraph;
