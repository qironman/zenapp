// Chapter list sidebar component

import { useMemo } from 'react';
import type { Chapter } from '../types';
import { extractToc, type TocItem } from '../lib/toc';

interface ChapterListProps {
  chapters: Chapter[];
  selectedSlug: string | null;
  currentContent: string;  // Add current chapter content for TOC
  onSelect: (slug: string) => void;
  onCreateNew: () => void;
  visible: boolean;
  onClose: () => void;
}

export function ChapterList({ 
  chapters, 
  selectedSlug, 
  currentContent,
  onSelect, 
  onCreateNew,
  visible,
  onClose,
}: ChapterListProps) {
  // Extract TOC from current chapter
  const toc = useMemo(() => {
    if (!selectedSlug || !currentContent) return [];
    return extractToc(currentContent);
  }, [selectedSlug, currentContent]);

  const handleTocClick = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      onClose();
    }
  };

  return (
    <div className={`chapter-list ${visible ? 'visible' : ''}`}>
      <div className="chapter-list-header">
        <h3>Chapters</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      <ul>
        {chapters.map((chapter) => (
          <li key={chapter.slug}>
            <div
              className={`chapter-item ${chapter.slug === selectedSlug ? 'selected' : ''}`}
              onClick={() => {
                onSelect(chapter.slug);
                onClose();
              }}
            >
              {chapter.title}
            </div>
            
            {/* Show TOC for selected chapter */}
            {chapter.slug === selectedSlug && toc.length > 0 && (
              <ul className="toc">
                {toc.map((item, idx) => (
                  <li
                    key={idx}
                    className={`toc-item toc-level-${item.level}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTocClick(item.id);
                    }}
                  >
                    {item.text}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
      <button className="new-chapter-btn" onClick={onCreateNew}>+ New Chapter</button>
    </div>
  );
}
