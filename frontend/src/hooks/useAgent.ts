// Hook for AI-powered text editing

import { useState, useCallback } from 'react';
import { streamAgentSuggestion, streamAgentRevision, approveEdit } from '../lib/api';

interface UseAgentOptions {
  bookSlug: string | null;
  chapterSlug: string | null;
  onEditApplied?: () => void;
  onSuggestionComplete?: (suggestion: string) => void;
}

export function useAgent({ bookSlug, chapterSlug, onEditApplied, onSuggestionComplete }: UseAgentOptions) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Process SSE stream and update state
  const processStream = useCallback(async (
    stream: AsyncGenerator<{ type: string; data: Record<string, string> }>
  ) => {
    let fullText = '';
    
    for await (const event of stream) {
      if (event.type === 'delta' && event.data.text) {
        fullText += event.data.text;
        setStreamedText(fullText);
      } else if (event.type === 'done' && event.data.replacement) {
        setStreamedText(event.data.replacement);
        fullText = event.data.replacement;
      } else if (event.type === 'session' && event.data.sessionId) {
        setSessionId(event.data.sessionId);
      } else if (event.type === 'error') {
        setError(event.data.error || 'Unknown error');
      }
    }
    
    // Auto-apply suggestion when streaming completes
    if (fullText && onSuggestionComplete) {
      onSuggestionComplete(fullText);
    }
  }, [onSuggestionComplete]);

  // Get initial suggestion
  const getSuggestion = useCallback(async (
    selectionStart: number,
    selectionEnd: number,
    prompt: string,
    provider: 'anthropic' | 'openai' = 'anthropic',
    content?: string  // Optional: current edited content
  ) => {
    if (!bookSlug || !chapterSlug) return;
    
    console.log('getSuggestion called:', { bookSlug, chapterSlug, selectionStart, selectionEnd, prompt, hasContent: !!content });
    
    setIsStreaming(true);
    setStreamedText('');
    setSessionId(null);
    setError(null);

    try {
      await processStream(streamAgentSuggestion({
        bookSlug,
        chapterSlug,
        selectionStart,
        selectionEnd,
        prompt,
        provider,
        content,  // Pass current content if provided
      }));
    } catch (e) {
      console.error('getSuggestion error:', e);
      setError(e instanceof Error ? e.message : 'Agent request failed');
    } finally {
      setIsStreaming(false);
    }
  }, [bookSlug, chapterSlug, processStream]);

  // Revise existing suggestion
  const reviseSuggestion = useCallback(async (
    prompt: string,
    provider: 'anthropic' | 'openai' = 'anthropic'
  ) => {
    if (!sessionId) return;
    
    setIsStreaming(true);
    setStreamedText('');
    setError(null);

    try {
      await processStream(streamAgentRevision({
        sessionId,
        prompt,
        provider,
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Revision request failed');
    } finally {
      setIsStreaming(false);
    }
  }, [sessionId, processStream]);

  // Approve and save
  const approve = useCallback(async () => {
    if (!sessionId || !bookSlug || !chapterSlug) return;
    
    try {
      await approveEdit(sessionId, bookSlug, chapterSlug);
      setSessionId(null);
      setStreamedText('');
      onEditApplied?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to apply edit');
    }
  }, [sessionId, bookSlug, chapterSlug, onEditApplied]);

  // Discard current suggestion (clear session, stay in panel to try again)
  const discard = useCallback(() => {
    setStreamedText('');
    setSessionId(null);
    setError(null);
    // Note: backend session will expire on its own, no need to call API
  }, []);

  // Reset state completely (e.g., when closing panel)
  const reset = useCallback(() => {
    setStreamedText('');
    setSessionId(null);
    setError(null);
  }, []);

  return {
    isStreaming,
    streamedText,
    sessionId,
    error,
    getSuggestion,
    reviseSuggestion,
    approve,
    discard,
    reset,
  };
}
