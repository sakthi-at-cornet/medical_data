/**
 * TypeScript types for the analytics UI.
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChartData {
  chart_type: 'bar' | 'line' | 'table' | 'donut' | 'gauge' | 'grouped_bar' | 'kpi';
  data: Array<Record<string, any>> | { labels: string[]; datasets: any[] };
  x_axis?: string;
  y_axis?: string;
  title?: string;
  options?: any; // Chart.js options from backend
  centerValue?: number; // For gauge charts
}

export interface ChatResponse {
  message: string;
  session_id: string;
  chart?: ChartData;
  insights?: string[];
  suggested_questions?: string[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  cubejs_connected: boolean;
}

export interface AgentInfo {
  name: string;
  status: 'active' | 'inactive';
  description: string;
  provider?: string;
  tools: string[];
  memory_enabled: boolean;
}

export interface AgentListResponse {
  agents: AgentInfo[];
  total_count: number;
}
