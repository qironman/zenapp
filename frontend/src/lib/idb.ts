// IndexedDB helpers for offline storage
// Simplified for read-only workflow (agent edits on backend)

import { openDB, type DBSchema, type IDBPDatabase } from 'idb';
import type { Draft } from '../types';

interface ZenAppDB extends DBSchema {
  drafts: {
    key: string;
    value: Draft;
  };
}

let db: IDBPDatabase<ZenAppDB> | null = null;

async function getDB(): Promise<IDBPDatabase<ZenAppDB>> {
  if (!db) {
    db = await openDB<ZenAppDB>('zenapp', 1, {
      upgrade(database) {
        database.createObjectStore('drafts', { keyPath: 'key' });
      },
    });
  }
  return db;
}

// Cache content locally for offline viewing
export async function cacheContent(bookSlug: string, chapterSlug: string, content: string): Promise<void> {
  const database = await getDB();
  const key = `${bookSlug}/${chapterSlug}`;
  
  await database.put('drafts', {
    key,
    content,
    savedAt: Date.now(),
  });
}

export async function getCachedContent(bookSlug: string, chapterSlug: string): Promise<Draft | undefined> {
  const database = await getDB();
  return database.get('drafts', `${bookSlug}/${chapterSlug}`);
}
