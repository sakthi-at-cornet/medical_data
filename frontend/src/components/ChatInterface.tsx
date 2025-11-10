'use client';

import React, { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { ChatMessage as ChatMessageType } from '@/types';
import { ChatMessage } from './ChatMessage';

interface MessageWithExtras extends ChatMessageType {
  chart?: any;
  insights?: string[];
}

const EXAMPLE_QUESTIONS = [
  "What's the OEE for each press line?",
  "Which part family has the best quality?",
  "Show me defect trends over time",
  "Compare shift performance",
];

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<MessageWithExtras[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>(EXAMPLE_QUESTIONS);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || loading) return;

    const userMessage: MessageWithExtras = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.sendMessage({
        message: messageText,
        session_id: sessionId || undefined,
      });

      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage: MessageWithExtras = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        chart: response.chart,
        insights: response.insights,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.suggested_questions) {
        setSuggestedQuestions(response.suggested_questions);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: MessageWithExtras = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleExampleClick = (question: string) => {
    handleSend(question);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="header-content">
          <div className="header-left">
            <img
              src="/praval_agentic_analytics.png"
              alt="Praval Agentic Analytics"
              className="main-logo"
            />
            <div className="header-text">
              <h1>Praval Agentic Analytics</h1>
              <p>Ask questions about press operations, OEE, part quality, and shift performance</p>
            </div>
          </div>
          <img
            src="/praval-logo.png"
            alt="Praval"
            className="praval-logo"
          />
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to Praval Agentic Analytics</h2>
            <p>Try asking:</p>
            <div className="example-questions">
              {EXAMPLE_QUESTIONS.map((question, idx) => (
                <button
                  key={idx}
                  className="example-button"
                  onClick={() => handleExampleClick(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <ChatMessage
            key={idx}
            message={msg}
            chart={msg.chart}
            insights={msg.insights}
          />
        ))}

        {loading && (
          <div className="loading-message">
            <span className="loading-spinner">●</span>
            <span>Analyzing data...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {suggestedQuestions.length > 0 && messages.length > 0 && !loading && (
        <div className="suggested-questions">
          <span className="suggestion-label">Try asking:</span>
          {suggestedQuestions.map((question, idx) => (
            <button
              key={idx}
              className="suggestion-button"
              onClick={() => handleExampleClick(question)}
            >
              {question}
            </button>
          ))}
        </div>
      )}

      <div className="input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about production data..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <button
          className="send-button"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};
