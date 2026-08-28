import React from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  UserCheck, 
  GitFork, 
  Activity, 
  Search, 
  AlertTriangle 
} from 'lucide-react';

const Navbar = ({ currentPage, setCurrentPage }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'agents', label: 'Agent Explorer', icon: UserCheck },
    { id: 'paths', label: 'Risk Paths', icon: GitFork },
    { id: 'blast', label: 'Blast Radius', icon: Activity },
    { id: 'violations', label: 'Policy Violations', icon: AlertTriangle },
    { id: 'graph', label: 'Graph Explorer', icon: Search }
  ];

  return (
    <div className="sidebar">
      <div className="logo">
        <ShieldAlert size={24} color="#00f0ff" />
        <span>Agent<span>Shield</span></span>
      </div>
      
      <ul className="nav-links">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <li key={item.id}>
              <a
                className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
              >
                <Icon size={18} />
                {item.label}
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Navbar;
