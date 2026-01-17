'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AgentInfo } from '@/types';

interface Dataset {
  name: string;
  description: string;
  icon: string;
}

const datasets: Dataset[] = [
  {
    name: 'RadiologyAudits',
    description: 'Quality audit data for CT & MRI imaging reports',
    icon: '🩻',
  },
  {
    name: 'Quality Metrics',
    description: 'CAT ratings, Star scores, Safety & Quality scores',
    icon: '⭐',
  },
  {
    name: 'Performance Analytics',
    description: 'Radiologist & Reviewer performance metrics',
    icon: '📊',
  },
];

export const LeftSidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState<'datasets' | 'agents'>('datasets');
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [isLoadingAgents, setIsLoadingAgents] = useState(false);
  const [agentsError, setAgentsError] = useState<string | null>(null);

  // Fetch agents on component mount
  useEffect(() => {
    const fetchAgents = async () => {
      setIsLoadingAgents(true);
      setAgentsError(null);
      try {
        const response = await api.getAgents();
        // Defensive check: ensure agents is an array
        const agentsList = Array.isArray(response?.agents) ? response.agents : [];
        setAgents(agentsList);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
        setAgentsError('Failed to load agents');
        setAgents([]); // Reset to empty array on error
      } finally {
        setIsLoadingAgents(false);
      }
    };

    fetchAgents();
  }, []);

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
            {isLoadingAgents && (
              <div className="loading-message">Loading agents...</div>
            )}
            {agentsError && (
              <div className="error-message">{agentsError}</div>
            )}
            {!isLoadingAgents && !agentsError && agents.length === 0 && (
              <div className="info-message">No agents registered</div>
            )}
            {!isLoadingAgents && agents.map((agent, idx) => (
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
