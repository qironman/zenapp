// Agent panel for AI-powered editing

import { useState, useEffect } from 'react';
import { getPrompts } from '../lib/api';

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
  const [prompts, setPrompts] = useState<string[]>([]);
  const [showCustom, setShowCustom] = useState(false);
  
  // Load prompts when panel becomes visible (always reload for fresh start)
  useEffect(() => {
    if (visible) {
      if (!hasSession) {
        // Reset to prompt selection mode when opening without a session
        setShowCustom(false);
        setPrompt('');
        getPrompts().then(setPrompts).catch(console.error);
      }
    }
  }, [visible, hasSession]);
  
  if (!visible) return null;

  const handlePromptSelect = (selectedPrompt: string) => {
    onSubmit(selectedPrompt);
  };

  const handleCustomSubmit = (e: React.FormEvent<HTMLFormElement>) => {
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

        {/* Show pre-defined prompts or custom input */}
        {!hasSession && !showCustom && prompts.length > 0 ? (
          <>
            <div className="prompt-list">
              <label>Choose an action:</label>
              {prompts.map((p, i) => (
                <button
                  key={i}
                  className="prompt-option"
                  onClick={() => handlePromptSelect(p)}
                  disabled={isStreaming}
                >
                  {p}
                </button>
              ))}
            </div>
            <button className="custom-prompt-btn" onClick={() => setShowCustom(true)}>
              Custom prompt...
            </button>
          </>
        ) : (
          <form onSubmit={handleCustomSubmit}>
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
        )}

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
