import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import AgentExplorer from './pages/AgentExplorer';
import RiskPaths from './pages/RiskPaths';
import BlastRadius from './pages/BlastRadius';
import PolicyViolations from './pages/PolicyViolations';
import GraphExplorer from './pages/GraphExplorer';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard setCurrentPage={setCurrentPage} />;
      case 'agents':
        return <AgentExplorer />;
      case 'paths':
        return <RiskPaths />;
      case 'blast':
        return <BlastRadius />;
      case 'violations':
        return <PolicyViolations />;
      case 'graph':
        return <GraphExplorer />;
      default:
        return <Dashboard setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="app-container">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
