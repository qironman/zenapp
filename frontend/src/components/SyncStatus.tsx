// Sync status indicator component

interface SyncStatusProps {
  dirty: boolean;
  saving: boolean;
  lastSaved: Date | null;
  error: string | null;
  onSaveNow: () => void;
}

export function SyncStatus({ dirty, saving, lastSaved, error, onSaveNow }: SyncStatusProps) {
  let status: string;
  let className = 'sync-status';

  if (error) {
    status = error;
    className += ' error';
  } else if (saving) {
    status = 'Saving...';
    className += ' saving';
  } else if (dirty) {
    status = 'Unsaved changes';
    className += ' dirty';
  } else if (lastSaved) {
    status = `Saved ${formatTime(lastSaved)}`;
    className += ' saved';
  } else {
    status = 'Ready';
    className += ' ready';
  }

  return (
    <div className={className}>
      <span>{status}</span>
      {dirty && !saving && (
        <button onClick={onSaveNow}>Sync now</button>
      )}
    </div>
  );
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  return date.toLocaleTimeString();
}
