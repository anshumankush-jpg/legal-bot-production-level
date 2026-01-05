# Artillity Frontend

A clean, modern web frontend for the Artillity multi-modal embedding server.

## Features

- 📤 **File Upload** - Upload text, documents, CSVs, or images
- 🔍 **Semantic Search** - Ask questions about your uploaded files
- 💬 **Chat Interface** - GPT-style chat UI
- 🎨 **Dark Theme** - Modern, clean design
- 📱 **Responsive** - Works on desktop and mobile

## Quick Start

### 1. Start the Backend

Make sure the Artillity backend is running:

```bash
python api_server.py
```

The backend should be available at `http://localhost:8000`

### 2. Start the Frontend

Open a terminal in the `frontend/` directory and run:

```bash
cd frontend
python -m http.server 5500
```

Or use any other static file server:
- Node.js: `npx http-server -p 5500`
- PHP: `php -S localhost:5500`

### 3. Open in Browser

Visit: **http://localhost:5500**

## Usage

1. **Upload Files** (Left Panel)
   - Click "Choose files..." or drag and drop
   - Select text, PDF, DOCX, CSV, or image files
   - Click "Upload & Index"
   - Wait for confirmation messages

2. **Search** (Right Panel)
   - Type your question in the input box
   - Press Enter or click "Send"
   - View results with source file information

## File Structure

```
frontend/
├── index.html      # Main HTML layout
├── styles.css      # Dark theme styling
├── app.js          # JavaScript logic
└── README.md       # This file
```

## API Endpoints

The frontend calls these backend endpoints:

- `POST /api/artillity/upload` - Upload and index files
- `POST /api/artillity/search` - Search indexed content

## Configuration

To change the backend URL, edit `app.js`:

```javascript
const API_BASE = "http://localhost:8000/api/artillity";
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Features

- ✅ Auto content detection
- ✅ Multi-file upload
- ✅ Real-time status updates
- ✅ Search results with previews
- ✅ Source file attribution
- ✅ Error handling
- ✅ Loading states

## Troubleshooting

### CORS Errors

If you see CORS errors, make sure:
- Backend CORS is enabled (already configured in `api_server.py`)
- Backend is running on the expected port (8000)

### Connection Errors

- Check that backend is running: `http://localhost:8000`
- Verify API_BASE URL in `app.js`
- Check browser console for detailed errors

### Files Not Uploading

- Check file size limits
- Verify file types are supported
- Check backend logs for errors

---

**Built for Artillity - Multi-Modal Embedding Engine** 🚀

