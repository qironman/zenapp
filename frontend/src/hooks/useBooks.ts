// Hook for fetching and managing books

import { useState, useEffect, useCallback } from 'react';
import { fetchBooks, fetchBook, createBook } from '../lib/api';
import type { Book } from '../types';

export function useBooks() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchBooks();
      setBooks(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load books');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = useCallback(async (title: string, author = '') => {
    const book = await createBook(title, author);
    await load();
    return book;
  }, [load]);

  return { books, loading, error, reload: load, create };
}

export function useBook(slug: string | null) {
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      setBook(null);
      return;
    }

    setLoading(true);
    fetchBook(slug)
      .then(data => {
        setBook(data);
        setError(null);
      })
      .catch(e => {
        setError(e instanceof Error ? e.message : 'Failed to load book');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [slug]);

  return { book, loading, error };
}
