'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage as ChatMessageType, ChartData } from '@/types';
import { Chart } from './Chart';

interface ChatMessageProps {
  message: ChatMessageType;
  chart?: ChartData;
  insights?: string[];
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  chart,
  insights,
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'Assistant'}</span>
        {message.timestamp && (
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>

      <div className="message-content markdown-content">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>

      {chart && (
        <div className="message-chart">
          <Chart chartData={chart} />
        </div>
      )}
    </div>
  );
};
