// API client for ZenApp backend

import type { Book, ChapterContent } from '../types';

const API_BASE = '/api';

// --- Auth ---

const TOKEN_KEY = 'zenapp_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(username: string, password: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  setToken(data.access_token);
  return true;
}

export function logout(): void {
  clearToken();
}

// --- Books ---

export async function fetchBooks(): Promise<Book[]> {
  const res = await fetch(`${API_BASE}/books`, { headers: authHeaders() });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to fetch books');
  return res.json();
}

export async function fetchBook(slug: string): Promise<Book> {
  const res = await fetch(`${API_BASE}/books/${slug}`, { headers: authHeaders() });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to fetch book');
  return res.json();
}

export async function createBook(title: string, author = ''): Promise<Book> {
  const res = await fetch(`${API_BASE}/books`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ title, author }),
  });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to create book');
  return res.json();
}

// --- Chapters ---

export async function fetchChapter(bookSlug: string, chapterSlug: string): Promise<ChapterContent> {
  const res = await fetch(`${API_BASE}/books/${bookSlug}/chapters/${chapterSlug}`, { headers: authHeaders() });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to fetch chapter');
  return res.json();
}

export async function createChapter(bookSlug: string, title: string): Promise<{ slug: string }> {
  const res = await fetch(`${API_BASE}/books/${bookSlug}/chapters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ title }),
  });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to create chapter');
  return res.json();
}

export async function saveChapter(bookSlug: string, chapterSlug: string, content: string): Promise<void> {
  const res = await fetch(`${API_BASE}/books/${bookSlug}/chapters/${chapterSlug}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ content }),
  });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to save chapter');
}

// --- Agent ---

export interface AgentSuggestRequest {
  bookSlug: string;
  chapterSlug: string;
  selectionStart: number;
  selectionEnd: number;
  prompt: string;
  provider?: 'anthropic' | 'openai';
  content?: string;  // Optional: use this content instead of fetching from backend
}

export interface AgentReviseRequest {
  sessionId: string;
  prompt: string;
  provider?: 'anthropic' | 'openai';
}

async function* parseSSEStream(response: Response): AsyncGenerator<{ type: string; data: Record<string, string> }> {
  if (!response.body) throw new Error('No response body');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let eventType = '';
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.slice(7);
      } else if (line.startsWith('data: ') && eventType) {
        try {
          const data = JSON.parse(line.slice(6));
          yield { type: eventType, data };
        } catch {
          // Skip malformed JSON
        }
        eventType = '';
      }
    }
  }
}

export async function* streamAgentSuggestion(req: AgentSuggestRequest): AsyncGenerator<{ type: string; data: Record<string, string> }> {
  console.log('streamAgentSuggestion called with:', { ...req, content: req.content ? `${req.content.length} chars` : 'none' });
  
  const res = await fetch(`${API_BASE}/agent/suggest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(req),
  });

  console.log('Response status:', res.status, res.statusText);
  
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Agent request failed');
  yield* parseSSEStream(res);
}

export async function* streamAgentRevision(req: AgentReviseRequest): AsyncGenerator<{ type: string; data: Record<string, string> }> {
  const res = await fetch(`${API_BASE}/agent/revise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(req),
  });

  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Revision request failed');
  yield* parseSSEStream(res);
}

export async function approveEdit(sessionId: string, bookSlug: string, chapterSlug: string): Promise<{ status: string; updatedAt: string }> {
  const res = await fetch(`${API_BASE}/agent/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ sessionId, bookSlug, chapterSlug }),
  });
  if (res.status === 401) { clearToken(); throw new Error('Unauthorized'); }
  if (!res.ok) throw new Error('Failed to approve edit');
  return res.json();
}
