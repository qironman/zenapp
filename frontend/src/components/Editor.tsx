// CodeMirror 6 Markdown editor component

import { useEffect, useRef, useCallback } from 'react';
import { EditorState } from '@codemirror/state';
import { EditorView, keymap } from '@codemirror/view';
import { markdown } from '@codemirror/lang-markdown';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { basicSetup } from 'codemirror';

interface EditorProps {
  content: string;
  onChange: (content: string) => void;
  onSelectionChange?: (from: number, to: number, text: string) => void;
  disabled?: boolean;
}

export function Editor({ content, onChange, onSelectionChange, disabled }: EditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const isExternalUpdate = useRef(false);

  // Create editor
  useEffect(() => {
    if (!containerRef.current) return;

    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged && !isExternalUpdate.current) {
        onChange(update.state.doc.toString());
      }
      
      if (update.selectionSet && onSelectionChange) {
        const { from, to } = update.state.selection.main;
        const text = update.state.sliceDoc(from, to);
        onSelectionChange(from, to, text);
      }
    });

    const state = EditorState.create({
      doc: content,
      extensions: [
        basicSetup,
        markdown(),
        history(),
        keymap.of([...defaultKeymap, ...historyKeymap]),
        updateListener,
        EditorView.lineWrapping,
        EditorView.theme({
          '&': { height: '100%' },
          '.cm-scroller': { overflow: 'auto' },
          '.cm-content': { 
            fontFamily: 'system-ui, sans-serif',
            fontSize: '16px',
            lineHeight: '1.6',
            padding: '16px',
          },
        }),
        EditorState.readOnly.of(disabled || false),
      ],
    });

    const view = new EditorView({
      state,
      parent: containerRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
      viewRef.current = null;
    };
  }, []);  // Only run once on mount

  // Update content when prop changes (external update)
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;

    const currentContent = view.state.doc.toString();
    if (content !== currentContent) {
      isExternalUpdate.current = true;
      view.dispatch({
        changes: { from: 0, to: currentContent.length, insert: content },
      });
      isExternalUpdate.current = false;
    }
  }, [content]);

  // Public method to replace selection
  const replaceSelection = useCallback((from: number, to: number, text: string) => {
    const view = viewRef.current;
    if (!view) return;

    view.dispatch({
      changes: { from, to, insert: text },
    });
  }, []);

  // Expose replaceSelection via ref (for parent component)
  useEffect(() => {
    (containerRef.current as HTMLDivElement & { replaceSelection?: typeof replaceSelection }).replaceSelection = replaceSelection;
  }, [replaceSelection]);

  return <div ref={containerRef} className="editor-container" />;
}
