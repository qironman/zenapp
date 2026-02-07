// Book picker dropdown component

import type { Book } from '../types';

interface BookPickerProps {
  books: Book[];
  selectedSlug: string | null;
  onSelect: (slug: string) => void;
  onCreateNew: () => void;
  loading?: boolean;
}

export function BookPicker({ books, selectedSlug, onSelect, onCreateNew, loading }: BookPickerProps) {
  return (
    <div className="book-picker">
      <select
        value={selectedSlug || ''}
        onChange={(e) => onSelect(e.target.value)}
        disabled={loading}
      >
        <option value="" disabled>Select a book...</option>
        {books.map((book) => (
          <option key={book.slug} value={book.slug}>
            {book.title}
          </option>
        ))}
      </select>
      <button 
        className="new-book-btn" 
        onClick={onCreateNew}
        disabled={loading}
        title="Create new book"
      >
        +
      </button>
    </div>
  );
}
