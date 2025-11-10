'use client';

import React, { useState } from 'react';

interface Dataset {
  name: string;
  description: string;
  icon: string;
}

interface Agent {
  name: string;
  status: 'active' | 'inactive';
  description: string;
}

const datasets: Dataset[] = [
  {
    name: 'PressOperations',
    description: 'Production-level press data with traceability',
    icon: '🏭',
  },
  {
    name: 'PartFamilyPerformance',
    description: 'Door vs Bonnet performance metrics',
    icon: '🚗',
  },
  {
    name: 'PressLineUtilization',
    description: 'Line capacity & shift analysis',
    icon: '⚙️',
  },
];

const agents: Agent[] = [
  {
    name: 'Chat Agent',
    status: 'active',
    description: 'Context & conversation flow',
  },
  {
    name: 'Data Analyst Agent',
    status: 'active',
    description: 'NL → Query translation',
  },
];

export const LeftSidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState<'datasets' | 'agents'>('datasets');

  if (isCollapsed) {
    return (
      <div className="sidebar left-sidebar collapsed">
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(false)}
          title="Expand sidebar"
        >
          ▶
        </button>
      </div>
    );
  }

  return (
    <div className="sidebar left-sidebar">
      <div className="sidebar-header">
        <h3>Data & Agents</h3>
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(true)}
          title="Collapse sidebar"
        >
          ◀
        </button>
      </div>

      <div className="sidebar-tabs">
        <button
          className={`tab ${activeSection === 'datasets' ? 'active' : ''}`}
          onClick={() => setActiveSection('datasets')}
        >
          Datasets
        </button>
        <button
          className={`tab ${activeSection === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveSection('agents')}
        >
          Agents
        </button>
      </div>

      <div className="sidebar-content">
        {activeSection === 'datasets' && (
          <div className="section">
            {datasets.map((dataset, idx) => (
              <div key={idx} className="item">
                <div className="item-header">
                  <span className="item-icon">{dataset.icon}</span>
                  <span className="item-name">{dataset.name}</span>
                </div>
                <p className="item-description">{dataset.description}</p>
              </div>
            ))}
          </div>
        )}

        {activeSection === 'agents' && (
          <div className="section">
            {agents.map((agent, idx) => (
              <div key={idx} className="item">
                <div className="item-header">
                  <span className={`status-dot ${agent.status}`}></span>
                  <span className="item-name">{agent.name}</span>
                </div>
                <p className="item-description">{agent.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
