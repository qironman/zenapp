// Type definitions for ZenApp

export interface Book {
  slug: string;
  title: string;
  author?: string;
  chapters?: Chapter[];
}

export interface Chapter {
  slug: string;
  title: string;
}

export interface ChapterContent {
  content: string;
  updatedAt: string;
}

export interface Draft {
  key: string;           // "book-slug/chapter-slug"
  content: string;
  savedAt: number;
}

export interface AgentSession {
  sessionId: string;
  replacement: string;
}
