// Extract table of contents from markdown content

export interface TocItem {
  text: string;
  level: number;
  id: string;
}

export function extractToc(markdown: string): TocItem[] {
  const lines = markdown.split('\n');
  const toc: TocItem[] = [];
  
  for (const line of lines) {
    // Match markdown headings (## or ###)
    const match = line.match(/^(#{2,3})\s+(.+)$/);
    if (match) {
      const level = match[1].length;
      const text = match[2].trim();
      const id = slugify(text);
      
      // Only include h2 and h3
      if (level === 2 || level === 3) {
        toc.push({ text, level, id });
      }
    }
  }
  
  return toc;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5\s-]/g, '') // Preserve Chinese characters
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}
