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
import {
  createChapter,
  fetchXiaohongshuStatus,
  isAuthenticated,
  logout,
  publishToXiaohongshu,
  saveChapter,
  uploadImage,
  type XiaohongshuPublishStatus,
} from './lib/api';

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
  const [isPublishingXhs, setIsPublishingXhs] = useState(false);
  const [xhsStatus, setXhsStatus] = useState<XiaohongshuPublishStatus | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Data hooks
  const { books, loading: booksLoading, create: createBook, error: booksError } = useBooks();
  const { book, loading: bookLoading, reload: reloadBook } = useBook(selectedBookSlug);
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
    setXhsStatus(null);
  }, []);

  const handleBookSelect = useCallback((slug: string) => {
    setSelectedBookSlug(slug);
    setSelectedChapterSlug(null);
    setXhsStatus(null);
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
    setXhsStatus(null);
  }, [resetAgent]);

  const handleCreateChapter = useCallback(async () => {
    if (!selectedBookSlug) return;
    const title = prompt('Chapter title:');
    if (title) {
      const chapter = await createChapter(selectedBookSlug, title);
      await reloadBook();
      setSelectedChapterSlug(chapter.slug);
    }
  }, [selectedBookSlug, reloadBook]);

  const handleContentChange = useCallback((newContent: string) => {
    setEditedContent(newContent);
    setHasUnsavedChanges(newContent !== content);
  }, [content]);

  const loadXhsStatus = useCallback(async () => {
    if (!selectedBookSlug || !selectedChapterSlug) {
      setXhsStatus(null);
      return;
    }

    try {
      const status = await fetchXiaohongshuStatus(selectedBookSlug, selectedChapterSlug);
      setXhsStatus(status);
    } catch (error) {
      console.error('Failed to load Xiaohongshu status:', error);
      setXhsStatus(null);
    }
  }, [selectedBookSlug, selectedChapterSlug]);

  const handleSave = useCallback(async () => {
    if (!selectedBookSlug || !selectedChapterSlug || !hasUnsavedChanges || isUploadingImage) return;
    
    setIsSaving(true);
    try {
      const result = await saveChapter(selectedBookSlug, selectedChapterSlug, editedContent);
      const nextSlug = result.chapterSlug || selectedChapterSlug;
      const renamed = !!result.renamed && nextSlug !== selectedChapterSlug;
      setHasUnsavedChanges(false);
      if (renamed) {
        setSelectedChapterSlug(nextSlug);
      }
      
      // Show success message
      if (renamed && result.gitCommitted) {
        setSaveMessage(`✓ Saved, renamed to ${nextSlug}, and pushed to git`);
      } else if (renamed) {
        setSaveMessage(`✓ Saved and renamed to ${nextSlug} (git commit failed)`);
      } else if (result.gitCommitted) {
        setSaveMessage('✓ Saved and pushed to git');
      } else {
        setSaveMessage('✓ Saved (git commit failed)');
      }
      
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(null), 3000);
      
      await reloadBook();
      if (!renamed) {
        await reloadChapter();  // Reload to get saved content
        await loadXhsStatus();
      }
    } catch (err) {
      console.error('Save failed:', err);
      setSaveMessage('✗ Save failed');
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsSaving(false);
    }
  }, [selectedBookSlug, selectedChapterSlug, editedContent, hasUnsavedChanges, isUploadingImage, reloadBook, reloadChapter, loadXhsStatus]);

  const handleImageUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0 || !selectedBookSlug) return;

    const maxImageSize = 5 * 1024 * 1024; // 5MB
    const validFiles = files.filter((file) => file.size <= maxImageSize);
    const skippedCount = files.length - validFiles.length;

    if (validFiles.length === 0) {
      setSaveMessage('✗ All selected images are too large (max 5MB)');
      setTimeout(() => setSaveMessage(null), 3000);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setIsUploadingImage(true);
    try {
      const uploadedUrls: string[] = [];
      let failedCount = 0;

      // Upload sequentially to preserve user-selected order in markdown insertion
      for (const file of validFiles) {
        try {
          const result = await uploadImage(selectedBookSlug, file);
          uploadedUrls.push(result.url);
        } catch (error) {
          failedCount += 1;
          console.error(`Image upload failed for ${file.name}:`, error);
        }
      }

      if (uploadedUrls.length > 0) {
        setEditedContent((prevContent) => {
          const lines = prevContent.split('\n');
          let insertLineIndex = 0;

          // Find first heading line (starts with #) and insert right after title
          for (let i = 0; i < lines.length; i++) {
            if (lines[i].trim().startsWith('#')) {
              insertLineIndex = i + 1;
              break;
            }
          }

          const imageLines: string[] = [];
          for (const url of uploadedUrls) {
            imageLines.push('', `![](${url})`, '');
          }

          lines.splice(insertLineIndex, 0, ...imageLines);
          return lines.join('\n');
        });
        setHasUnsavedChanges(true);
      }

      const successCount = uploadedUrls.length;
      if (successCount > 0 && failedCount === 0 && skippedCount === 0) {
        setSaveMessage(`✓ Inserted ${successCount} image${successCount > 1 ? 's' : ''}`);
      } else if (successCount > 0) {
        const failedTotal = failedCount + skippedCount;
        setSaveMessage(`⚠ Inserted ${successCount}; ${failedTotal} failed/skipped`);
      } else {
        setSaveMessage('✗ Upload failed');
      }
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsUploadingImage(false);
      // Reset file input so selecting the same files again still triggers onChange
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [selectedBookSlug]);

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

  useEffect(() => {
    loadXhsStatus();
  }, [loadXhsStatus]);

  const handleSelectionChange = useCallback((from: number, to: number, text: string) => {
    if (text.length > 0) {
      setSelection({ from, to, text });
    } else {
      setSelection(null);
    }
  }, []);

  const handlePublishToXhs = useCallback(async () => {
    if (!selectedBookSlug || !selectedChapterSlug) return;
    if (hasUnsavedChanges) {
      setSaveMessage('✗ Save chapter before publishing');
      setTimeout(() => setSaveMessage(null), 3000);
      return;
    }

    setIsPublishingXhs(true);
    try {
      const result = await publishToXiaohongshu(selectedBookSlug, selectedChapterSlug);
      setXhsStatus(result);

      if (result.status === 'prepared' && result.message) {
        setSaveMessage(result.message);
      } else if (result.operation === 'update') {
        setSaveMessage('✓ Xiaohongshu post updated');
      } else if (result.operation === 'create') {
        setSaveMessage('✓ Published to Xiaohongshu');
      } else if (result.message) {
        setSaveMessage(result.message);
      } else {
        setSaveMessage('✓ Publish completed');
      }
      setTimeout(() => setSaveMessage(null), 3500);
    } catch (error) {
      console.error('Xiaohongshu publish failed:', error);
      const msg = error instanceof Error ? error.message : 'Publish failed';
      setSaveMessage(`✗ ${msg}`);
      setTimeout(() => setSaveMessage(null), 3500);
    } finally {
      setIsPublishingXhs(false);
      await loadXhsStatus();
    }
  }, [selectedBookSlug, selectedChapterSlug, hasUnsavedChanges, loadXhsStatus]);

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
                    disabled={isSaving || isUploadingImage}
                    title={isUploadingImage ? 'Wait for image upload/link insertion to finish' : 'Save changes'}
                  >
                    {isSaving ? '💾 Saving...' : (isUploadingImage ? '🖼 Uploading...' : '💾 Save')}
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
                      multiple
                      onChange={handleImageUpload}
                      style={{ display: 'none' }}
                    />
                    <button 
                      className="image-fab" 
                      onClick={handleInsertImageClick}
                      disabled={isUploadingImage}
                      title="Insert image(s)"
                    >
                      {isUploadingImage ? '⏳' : '📷'}
                    </button>
                    <button
                      className="publish-fab"
                      onClick={handlePublishToXhs}
                      disabled={isPublishingXhs}
                      title={hasUnsavedChanges ? 'Save chapter first' : 'Publish this chapter to Xiaohongshu'}
                    >
                      {isPublishingXhs
                        ? '📮 Publishing...'
                        : xhsStatus?.published
                          ? (xhsStatus.needsUpdate ? '📮 Update 小红书' : '📮 Re-publish 小红书')
                          : '📮 Publish 小红书'}
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
