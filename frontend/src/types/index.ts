/**
 * TypeScript types for the analytics UI.
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChartData {
  chart_type: 'bar' | 'line' | 'table';
  data: Array<Record<string, any>>;
  x_axis?: string;
  y_axis?: string;
  title?: string;
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
