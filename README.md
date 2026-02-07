# ZenApp - AI-Powered Markdown Book Editor

A mobile-first Progressive Web App for writing and editing books in Markdown, where **AI is the writer** and **you are the director**.

## 🌟 Key Features

### 📝 Content Editing
- **Dual Mode**: Switch between Read mode (Kindle-like) and Edit mode (CodeMirror)
- **AI-Powered Editing**: Select text and use AI to rewrite, translate, or improve
- **Smart Selection**: "Select All for AI" button for whole-chapter edits
- **Pre-defined Prompts**: Quick access to common transformations (Vonnegut style, translation, etc.)
- **Iterative Refinement**: Suggest → Revise → Approve workflow
- **Native Spell Check**: iPhone's built-in spell checking in editor

### 📷 Image Management
- **Photo Upload**: Insert images from iPhone camera roll or photo library
- **Auto-Processing**: Resize to max 1200px, compress to 85% JPEG quality
- **Smart Placement**: Images inserted right below chapter title
- **Format Support**: JPG, PNG, HEIC (auto-converted to JPG), WebP
- **Size Limit**: 5MB max per image
- **Storage**: Images in backend/data/books/{book-slug}/images/ (excluded from git)

### 🎨 Kindle-Inspired Theme
- **Warm Paper Background**: Cream/beige (#f4f1ea) for comfortable reading
- **Serif Typography**: Bookerly, Georgia, Palatino font stack
- **Optimized Reading**: 700px max-width, 1.7 line-height, justified text
- **Minimal UI**: Subtle borders and shadows, understated interactions
- **Dark Text**: Charcoal (#3d3d3d) for excellent readability

### 📚 Book Organization
- **Multi-Book Library**: Create and manage multiple books
- **Chapter Management**: Add, reorder, and navigate chapters
- **Table of Contents**: Auto-generated from markdown headings
- **Auto-Commit**: Each save commits to git with descriptive message
- **Toast Notifications**: Visual feedback for save/upload operations

### 🔄 Reliability
- **Auto-Retry**: Network failures retry automatically (3 attempts with exponential backoff)
- **Session Management**: Maintains AI conversation context for refinements
- **Data Backup**: Full backend copy to /data4/zenapp/backend/

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/qironman/zenapp.git
cd zenapp

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install Pillow

# Frontend setup
cd ../frontend
npm install
npm run build

# Start backend
cd ../backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --port 8001 > /tmp/zenapp-backend.log 2>&1 &

# Access at http://localhost:8001
```

**Default credentials**: username: admin, password: zenapp123

## 📖 How to Use

### Basic Workflow
1. Login with credentials
2. Create/Select Book using the "+" button or dropdown
3. Add Chapters via sidebar
4. Switch to Edit Mode
5. Select Text you want to edit
6. Click "✨ AI Edit" or "✨ All" for entire chapter
7. Choose Prompt or write custom instruction
8. Review AI Suggestion (streams in real-time)
9. Revise (give more feedback) or Approve & Save
10. Switch to Read Mode to see formatted result

### Inserting Images
1. In Edit Mode, click the 📷 button
2. Choose photo from library or take new picture
3. Image uploads and inserts below chapter title
4. Save to persist changes
5. Image appears in Read mode

## 🏗️ Tech Stack

**Frontend**: React 18 + TypeScript + Vite + CodeMirror 6 + React-Markdown

**Backend**: FastAPI + LiteLLM + Pillow + File-based storage

**AI**: Copilot CLI or Codex CLI (no API keys needed)

## 🔌 API Endpoints

- POST /api/login - Authentication
- GET /api/books - List all books
- POST /api/books - Create new book
- GET /api/books/{slug} - Get book with chapters
- GET /api/books/{book}/chapters/{chapter} - Get chapter content
- PUT /api/books/{book}/chapters/{chapter} - Update chapter
- POST /api/books/{book}/images - Upload image
- GET /api/books/{book}/images/{filename} - Serve image
- POST /api/agent/suggest - Get AI edit suggestion (SSE)
- POST /api/agent/revise - Refine suggestion (SSE)
- POST /api/agent/approve - Apply edit and save
- GET /api/prompts - Get prompt templates
- POST /api/prompts - Update prompts

## 🐛 Troubleshooting

### "Load failed" errors
- Auto-retry will attempt 3 times with exponential backoff
- Check backend: curl http://localhost:8001/api/health
- View logs: tail -f /tmp/zenapp-backend.log

### Images not showing
- Ensure you clicked Save after upload
- Check images uploaded: ls backend/data/books/{book-slug}/images/

### Backend not accessible
- Restart: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001

## 📝 Recent Updates

- ✅ Kindle-inspired theme for comfortable reading
- ✅ Image upload with auto-resize and compression
- ✅ Smart image insertion below chapter title
- ✅ "Select All for AI" button
- ✅ Automatic retry logic for network failures
- ✅ Git auto-commit on every save
- ✅ Toast notifications
- ✅ Photo library selection
- ✅ Pre-defined AI prompt templates

## 🚧 Future Enhancements

- Export to WeChat 公众号
- Export to 小红书
- Drag-and-drop reordering
- Dark mode
- Offline PWA support
- ePub/PDF export

## 📄 License

MIT

## 👨‍💻 Author

Built with ❤️ using GitHub Copilot CLI
