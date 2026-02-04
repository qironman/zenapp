import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import type { Components } from 'react-markdown';

interface ReaderProps {
  content: string;
  onEditClick: () => void;
}

// Helper to extract text from react-markdown children
function extractText(children: any): string {
  if (typeof children === 'string') return children;
  if (Array.isArray(children)) {
    return children.map(extractText).join('');
  }
  if (children?.props?.children) {
    return extractText(children.props.children);
  }
  return String(children || '');
}

// Helper to generate heading IDs
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5\s-]/g, '') // Preserve Chinese characters
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

export function Reader({ content, onEditClick }: ReaderProps) {
  // Custom components to add IDs to headings
  const components: Components = {
    h2: ({ children, ...props }) => {
      const text = extractText(children);
      const id = slugify(text);
      return <h2 id={id} {...props}>{children}</h2>;
    },
    h3: ({ children, ...props }) => {
      const text = extractText(children);
      const id = slugify(text);
      return <h3 id={id} {...props}>{children}</h3>;
    },
  };

  return (
    <div className="reader-container">
      <div className="reader-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </div>
      <button className="edit-fab" onClick={onEditClick} title="Switch to edit mode">
        ✏️ Edit
      </button>
    </div>
  );
}
