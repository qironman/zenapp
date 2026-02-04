// Hook for fetching chapter content (read-only from server)

import { useState, useEffect, useCallback } from 'react';
import { fetchChapter } from '../lib/api';

interface UseChapterOptions {
  bookSlug: string | null;
  chapterSlug: string | null;
}

export function useChapter({ bookSlug, chapterSlug }: UseChapterOptions) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!bookSlug || !chapterSlug) {
      setContent('');
      return;
    }

    setLoading(true);
    try {
      const data = await fetchChapter(bookSlug, chapterSlug);
      setContent(data.content);
      setLastUpdated(data.updatedAt);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load chapter');
    } finally {
      setLoading(false);
    }
  }, [bookSlug, chapterSlug]);

  // Load on mount and when slug changes
  useEffect(() => {
    load();
  }, [load]);

  return {
    content,
    loading,
    error,
    lastUpdated,
    reload: load,  // Call this after agent applies an edit
  };
}
