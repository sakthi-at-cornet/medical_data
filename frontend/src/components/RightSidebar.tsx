'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface ComponentStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down' | 'checking';
  icon: string;
  description: string;
  details?: string;
}

export const RightSidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [components, setComponents] = useState<ComponentStatus[]>([
    {
      name: 'Agents API',
      status: 'checking',
      icon: '🤖',
      description: 'FastAPI + AI Agents',
    },
    {
      name: 'Cube.js',
      status: 'checking',
      icon: '📊',
      description: 'Metrics Layer',
    },
    {
      name: 'dbt / Airflow',
      status: 'checking',
      icon: '⚙️',
      description: 'Transformations & Orchestration',
    },
    {
      name: 'PostgreSQL DWH',
      status: 'checking',
      icon: '🗄️',
      description: 'Data Warehouse',
    },
    {
      name: 'Medical Data',
      status: 'checking',
      icon: '🏥',
      description: 'Radiology Audit Database',
    },
  ]);

  const [lastChecked, setLastChecked] = useState<string>('');

  const checkBackendStatus = async () => {
    try {
      const health = await api.healthCheck();

      setComponents((prev) =>
        prev.map((comp) => {
          if (comp.name === 'Agents API') {
            return {
              ...comp,
              status: health.status === 'healthy' ? 'healthy' : 'degraded',
              details: `v${health.version}`,
            };
          }
          if (comp.name === 'Cube.js') {
            return {
              ...comp,
              status: health.cubejs_connected ? 'healthy' : 'down',
            };
          }
          // For other components, assume healthy if agents are healthy
          if (health.status === 'healthy') {
            return { ...comp, status: 'healthy' };
          }
          return comp;
        })
      );

      setLastChecked(new Date().toLocaleTimeString());
    } catch (error) {
      setComponents((prev) =>
        prev.map((comp) => ({
          ...comp,
          status: 'down',
        }))
      );
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  if (isCollapsed) {
    return (
      <div className="sidebar right-sidebar collapsed">
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(false)}
          title="Expand status"
        >
          ◀
        </button>
      </div>
    );
  }

  return (
    <div className="sidebar right-sidebar">
      <div className="sidebar-header">
        <h3>System Status</h3>
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(true)}
          title="Collapse status"
        >
          ▶
        </button>
      </div>

      <div className="sidebar-content">
        <div className="status-grid">
          {components.map((component, idx) => (
            <div key={idx} className="status-card">
              <div className="status-card-header">
                <span className="status-icon">{component.icon}</span>
                <div className="status-info">
                  <div className="status-name">{component.name}</div>
                  <div className="status-description">{component.description}</div>
                </div>
              </div>
              <div className="status-indicator">
                <span className={`status-badge ${component.status}`}>
                  {component.status === 'checking' && '⏳'}
                  {component.status === 'healthy' && '✓'}
                  {component.status === 'degraded' && '⚠'}
                  {component.status === 'down' && '✗'}
                </span>
                <span className="status-text">
                  {component.status === 'checking' && 'Checking...'}
                  {component.status === 'healthy' && 'Healthy'}
                  {component.status === 'degraded' && 'Degraded'}
                  {component.status === 'down' && 'Down'}
                </span>
              </div>
              {component.details && (
                <div className="status-details">{component.details}</div>
              )}
            </div>
          ))}
        </div>

        <div className="status-footer">
          <button className="refresh-btn" onClick={checkBackendStatus}>
            🔄 Refresh
          </button>
          {lastChecked && (
            <span className="last-checked">Last checked: {lastChecked}</span>
          )}
        </div>
      </div>
    </div>
  );
};
