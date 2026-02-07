// Main App component

import { useState, useCallback, useEffect, useRef } from 'react';
import { useBooks, useBook } from './hooks/useBooks';
import { useChapter } from './hooks/useChapter';
import { useAgent } from './hooks/useAgent';
import { BookPicker } from './components/BookPicker';
import { ChapterList } from './components/ChapterList';
import { Editor } from './components/Editor';
import { Reader } from './components/Reader';
import { AgentPanel } from './components/AgentPanel';
import { LoginPage } from './components/LoginPage';
import { createChapter, isAuthenticated, logout, saveChapter, uploadImage } from './lib/api';

import './App.css';

export default function App() {
  // Auth state
  const [authenticated, setAuthenticated] = useState(isAuthenticated());

  // State
  const [selectedBookSlug, setSelectedBookSlug] = useState<string | null>(null);
  const [selectedChapterSlug, setSelectedChapterSlug] = useState<string | null>(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [selection, setSelection] = useState<{ from: number; to: number; text: string } | null>(null);
  const [agentPanelVisible, setAgentPanelVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);  // false = read mode (default)
  const scrollPositionRef = useRef(0);  // Track scroll position when switching modes
  const [editedContent, setEditedContent] = useState<string>('');  // Track manual edits
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Data hooks
  const { books, loading: booksLoading, create: createBook, error: booksError } = useBooks();
  const { book, loading: bookLoading } = useBook(selectedBookSlug);
  const { 
    content, 
    loading: chapterLoading, 
    error: chapterError,
    reload: reloadChapter,
  } = useChapter({ bookSlug: selectedBookSlug, chapterSlug: selectedChapterSlug });

  // Agent hook - reload chapter after edit is applied
  const { 
    isStreaming, 
    streamedText, 
    sessionId,
    error: agentError, 
    getSuggestion, 
    reviseSuggestion,
    approve,
    discard,
    reset: resetAgent,
  } = useAgent({
    bookSlug: selectedBookSlug,
    chapterSlug: selectedChapterSlug,
    onEditApplied: reloadChapter,
    onSuggestionComplete: useCallback((suggestion: string) => {
      // Auto-apply suggestion to edited content as soon as it arrives
      if (selection) {
        const before = editedContent.slice(0, selection.from);
        const after = editedContent.slice(selection.to);
        const newContent = before + suggestion + after;
        setEditedContent(newContent);
        setHasUnsavedChanges(true);
      }
    }, [selection, editedContent]),
  });

  // Handle auth errors (401)
  useEffect(() => {
    if (booksError === 'Unauthorized' || chapterError === 'Unauthorized') {
      setAuthenticated(false);
    }
  }, [booksError, chapterError]);

  // Handlers
  const handleLogin = useCallback(() => {
    setAuthenticated(true);
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    setAuthenticated(false);
    setSelectedBookSlug(null);
    setSelectedChapterSlug(null);
  }, []);

  const handleBookSelect = useCallback((slug: string) => {
    setSelectedBookSlug(slug);
    setSelectedChapterSlug(null);
    setSidebarVisible(true);  // Auto-open sidebar when book selected
  }, []);

  const handleCreateBook = useCallback(async () => {
    const title = prompt('Book title:');
    if (title) {
      const book = await createBook(title);
      setSelectedBookSlug(book.slug);
    }
  }, [createBook]);

  const handleChapterSelect = useCallback((slug: string) => {
    setSelectedChapterSlug(slug);
    setAgentPanelVisible(false);
    resetAgent();
    scrollPositionRef.current = 0;  // Reset scroll on chapter change
    setHasUnsavedChanges(false);  // Reset unsaved changes
    setEditedContent('');
  }, [resetAgent]);

  const handleCreateChapter = useCallback(async () => {
    if (!selectedBookSlug) return;
    const title = prompt('Chapter title:');
    if (title) {
      const chapter = await createChapter(selectedBookSlug, title);
      setSelectedChapterSlug(chapter.slug);
    }
  }, [selectedBookSlug]);

  const handleContentChange = useCallback((newContent: string) => {
    setEditedContent(newContent);
    setHasUnsavedChanges(newContent !== content);
  }, [content]);

  const handleSave = useCallback(async () => {
    if (!selectedBookSlug || !selectedChapterSlug || !hasUnsavedChanges) return;
    
    setIsSaving(true);
    try {
      const result = await saveChapter(selectedBookSlug, selectedChapterSlug, editedContent);
      setHasUnsavedChanges(false);
      
      // Show success message
      if (result.gitCommitted) {
        setSaveMessage('✓ Saved and pushed to git');
      } else {
        setSaveMessage('✓ Saved (git commit failed)');
      }
      
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(null), 3000);
      
      await reloadChapter();  // Reload to get saved content
    } catch (err) {
      console.error('Save failed:', err);
      setSaveMessage('✗ Save failed');
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsSaving(false);
    }
  }, [selectedBookSlug, selectedChapterSlug, editedContent, hasUnsavedChanges, reloadChapter]);

  const handleImageUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedBookSlug) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setSaveMessage('✗ Image too large (max 5MB)');
      setTimeout(() => setSaveMessage(null), 3000);
      return;
    }

    setIsUploadingImage(true);
    try {
      const result = await uploadImage(selectedBookSlug, file);
      
      // Insert markdown at cursor position or end of selection
      const insertPos = selection ? selection.to : editedContent.length;
      const markdownImage = `![](${result.url})`;
      
      const newContent = 
        editedContent.slice(0, insertPos) + 
        markdownImage + 
        editedContent.slice(insertPos);
      
      setEditedContent(newContent);
      setHasUnsavedChanges(true);
      
      setSaveMessage('✓ Image inserted');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Image upload failed:', error);
      setSaveMessage('✗ Upload failed');
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsUploadingImage(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [selectedBookSlug, selection, editedContent]);

  const handleInsertImageClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleToggleEditMode = useCallback(() => {
    // Save scroll position before switching
    const mainElement = document.querySelector('main');
    if (mainElement) {
      scrollPositionRef.current = mainElement.scrollTop;
    }
    setEditMode(prev => !prev);
  }, []);

  // Restore scroll position after mode switch
  useEffect(() => {
    if (scrollPositionRef.current > 0) {
      const mainElement = document.querySelector('main');
      if (mainElement) {
        // Need to wait for content to render
        setTimeout(() => {
          mainElement.scrollTop = scrollPositionRef.current;
        }, 50);
      }
    }
  }, [editMode]);

  // Sync editedContent when content loads
  useEffect(() => {
    if (content && !hasUnsavedChanges) {
      setEditedContent(content);
    }
  }, [content, hasUnsavedChanges]);

  const handleSelectionChange = useCallback((from: number, to: number, text: string) => {
    if (text.length > 0) {
      setSelection({ from, to, text });
    } else {
      setSelection(null);
    }
  }, []);

  const handleAgentSubmit = useCallback((prompt: string) => {
    if (!selection) return;
    // If we have unsaved edits, use the edited content; otherwise backend will fetch saved content
    const currentContent = hasUnsavedChanges ? editedContent : undefined;
    getSuggestion(selection.from, selection.to, prompt, 'anthropic', currentContent);
  }, [selection, getSuggestion, hasUnsavedChanges, editedContent]);

  const handleAgentRevise = useCallback((prompt: string) => {
    reviseSuggestion(prompt);
  }, [reviseSuggestion]);

  const handleAgentAccept = useCallback(async () => {
    // Suggestion already auto-applied, just close panel and clear state
    setAgentPanelVisible(false);
    setSelection(null);
    discard();  // Clear agent state
  }, [discard]);

  const handleAgentDiscard = useCallback(() => {
    discard();
    // Panel stays open, user can enter a new prompt
  }, [discard]);

  const handleAgentCancel = useCallback(() => {
    setAgentPanelVisible(false);
    resetAgent();
  }, [resetAgent]);

  const handleAIButtonClick = useCallback(() => {
    if (selection && selection.text.length > 0) {
      resetAgent();  // Clear any stale session state from previous interactions
      setAgentPanelVisible(true);
    }
  }, [selection, resetAgent]);

  const handleSelectAllForAI = useCallback(() => {
    if (!editedContent) return;
    
    // Set selection to entire content
    setSelection({
      from: 0,
      to: editedContent.length,
      text: editedContent
    });
    
    // Open AI panel
    resetAgent();
    setAgentPanelVisible(true);
  }, [editedContent, resetAgent]);

  // Show login page if not authenticated
  if (!authenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      {/* Toast notification for save feedback */}
      {saveMessage && (
        <div className="save-toast">
          {saveMessage}
        </div>
      )}

      {/* Header */}
      <header className="app-header">
        <button 
          className="menu-btn" 
          onClick={() => setSidebarVisible(!sidebarVisible)}
          disabled={!selectedBookSlug}
        >
          ☰
        </button>
        <BookPicker
          books={books}
          selectedSlug={selectedBookSlug}
          onSelect={handleBookSelect}
          onCreateNew={handleCreateBook}
          loading={booksLoading}
        />
        <button className="logout-btn" onClick={handleLogout} title="Sign out">
          ⎋
        </button>
      </header>

      {/* Sidebar */}
      <ChapterList
        chapters={bookLoading ? [] : (book?.chapters || [])}
        selectedSlug={selectedChapterSlug}
        currentContent={content}
        onSelect={handleChapterSelect}
        onCreateNew={handleCreateChapter}
        visible={sidebarVisible}
        onClose={() => setSidebarVisible(false)}
        loading={bookLoading}
      />

      {/* Main content */}
      <main className="app-main">
        {chapterLoading ? (
          <div className="loading">Loading...</div>
        ) : selectedChapterSlug ? (
          <>
            {editMode ? (
              <>
                <Editor
                  content={editedContent || content}
                  onChange={handleContentChange}
                  onSelectionChange={handleSelectionChange}
                  disabled={false}
                />
                
                {/* Save button */}
                {hasUnsavedChanges && (
                  <button 
                    className="save-fab" 
                    onClick={handleSave}
                    disabled={isSaving}
                    title="Save changes"
                  >
                    {isSaving ? '💾 Saving...' : '💾 Save'}
                  </button>
                )}
                
                {/* Floating AI button */}
                {selection && selection.text.length > 0 && !agentPanelVisible && (
                  <button className="ai-fab" onClick={handleAIButtonClick}>
                    ✨ AI Edit
                  </button>
                )}
                
                {/* Insert Image button */}
                {!agentPanelVisible && (
                  <>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleImageUpload}
                      style={{ display: 'none' }}
                    />
                    <button 
                      className="image-fab" 
                      onClick={handleInsertImageClick}
                      disabled={isUploadingImage}
                      title="Insert image"
                    >
                      {isUploadingImage ? '⏳' : '📷'}
                    </button>
                  </>
                )}
                
                {/* Select All for AI button - show when no selection */}
                {!agentPanelVisible && !selection && (
                  <button 
                    className="select-all-fab" 
                    onClick={handleSelectAllForAI}
                    title="Select all text for AI editing"
                  >
                    ✨ All
                  </button>
                )}
                
                {/* Switch to read mode */}
                {!agentPanelVisible && !selection && !hasUnsavedChanges && (
                  <button className="mode-fab" onClick={handleToggleEditMode} title="Switch to read mode">
                    📖 Read
                  </button>
                )}
              </>
            ) : (
              <Reader
                content={content}
                onEditClick={handleToggleEditMode}
              />
            )}
          </>
        ) : selectedBookSlug ? (
          null  // Sidebar is already open, no placeholder needed
        ) : (
          <div className="placeholder">
            <p>Select a book to get started</p>
          </div>
        )}
      </main>

      {/* Agent Panel (bottom sheet) */}
      <AgentPanel
        visible={agentPanelVisible}
        selectedText={selection?.text || ''}
        streamedText={streamedText}
        isStreaming={isStreaming}
        canApprove={!!sessionId && !isStreaming}
        hasSession={!!sessionId}
        error={agentError}
        onSubmit={handleAgentSubmit}
        onRevise={handleAgentRevise}
        onAccept={handleAgentAccept}
        onDiscard={handleAgentDiscard}
        onCancel={handleAgentCancel}
      />

      {/* Overlay for sidebar */}
      {sidebarVisible && (
        <div className="overlay" onClick={() => setSidebarVisible(false)} />
      )}
    </div>
  );
}
