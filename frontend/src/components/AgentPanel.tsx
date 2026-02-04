// Agent panel for AI-powered editing

import { useState } from 'react';

interface AgentPanelProps {
  visible: boolean;
  selectedText: string;
  streamedText: string;
  isStreaming: boolean;
  canApprove: boolean;
  hasSession: boolean;
  error: string | null;
  onSubmit: (prompt: string) => void;
  onRevise: (prompt: string) => void;
  onAccept: () => void;
  onDiscard: () => void;
  onCancel: () => void;
}

export function AgentPanel({
  visible,
  selectedText,
  streamedText,
  isStreaming,
  canApprove,
  hasSession,
  error,
  onSubmit,
  onRevise,
  onAccept,
  onDiscard,
  onCancel,
}: AgentPanelProps) {
  const [prompt, setPrompt] = useState('');
  
  if (!visible) return null;

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    if (hasSession) {
      onRevise(prompt.trim());
    } else {
      onSubmit(prompt.trim());
    }
    setPrompt('');
  };

  return (
    <div className="agent-panel">
      <div className="agent-panel-content">
        <div className="selected-text">
          <label>Selected text:</label>
          <p>{selectedText.length > 200 ? selectedText.slice(0, 200) + '...' : selectedText}</p>
        </div>

        {/* Prompt input */}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={hasSession ? "How should I revise this?" : "What should the AI do?"}
            autoFocus
            disabled={isStreaming}
          />
          <button type="submit" disabled={isStreaming || !prompt.trim()}>
            {isStreaming ? 'Thinking...' : hasSession ? 'Revise' : 'Suggest'}
          </button>
        </form>

        {/* Show streaming response */}
        {(streamedText || isStreaming) && (
          <div className="streamed-response">
            <label>AI suggestion:</label>
            <p>{streamedText || '...'}</p>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {/* Action buttons when we have a ready suggestion */}
        {canApprove && (
          <div className="agent-actions">
            <button className="accept-btn" onClick={onAccept}>
              ✓ Approve & Save
            </button>
            <button className="discard-btn" onClick={onDiscard}>
              ✗ Discard
            </button>
          </div>
        )}

        <button className="cancel-btn" onClick={onCancel}>Close</button>
      </div>
    </div>
  );
}
