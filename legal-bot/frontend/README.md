# weknowrights.CA Frontend

Angular-based frontend for the PLAZA-AI Legal RAG system. This is a modern, responsive web application that provides a ChatGPT-style interface for querying legal documents.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`
- Backend authentication configured (see `backend/IMPLEMENTATION_GUIDE.md`)

### New Features (Latest)
- 🔐 Authentication & Login
- 🌍 Language & Country Selection
- 🎫 Ticket/Summons Upload & Parsing
- 💬 Enhanced Chat with Structured Answers (FIGHT vs PAY options)
- ⚖️ Lawyer/Paralegal Listing

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm start
# or
ng serve
```

The app will be available at `http://localhost:4200`

### Build for Production

```bash
npm run build
```

Output will be in `dist/weknowrights-ca/`

---

## 🎯 New UX Flow

### Complete User Journey

1. **Login** (`/login`)
   - Email/password authentication
   - JWT token storage
   - Redirect to language selection

2. **Language Selection** (`/welcome`)
   - Choose language (EN, FR, HI, PA, ES, TA, ZH)
   - Select country (CA, US)
   - Save preferences
   - Redirect to chat

3. **Chat Interface** (`/chat`)
   - Upload ticket/document
   - Ask questions about tickets/summons
   - Receive structured answers with:
     - Offence & Demerit Points
     - Consequences
     - Option 1: Fight/Appeal
     - Option 2: Pay Fine
   - View lawyer/paralegal list

### New Components Required

- `LoginComponent` - Authentication page
- `WelcomeComponent` - Language/country selection
- Enhanced `ChatComponent` - Structured answer rendering
- `LawyerListComponent` - Legal professional directory

See `backend/IMPLEMENTATION_GUIDE.md` for complete requirements.

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.component.ts          # Main app component with navigation
│   │   ├── app.routes.ts             # Route configuration
│   │   ├── components/
│   │   │   ├── chat/                 # Chat interface component
│   │   │   ├── upload/               # Document upload component
│   │   │   ├── documents/            # Document library component
│   │   │   └── analytics/            # Analytics dashboard
│   │   └── services/
│   │       └── chat.service.ts      # API service for backend communication
│   ├── environments/
│   │   └── environment.ts           # Environment configuration
│   ├── index.html                    # Main HTML file
│   ├── main.ts                       # Application bootstrap
│   └── styles.scss                   # Global styles
├── angular.json                       # Angular CLI configuration
├── package.json                       # Dependencies and scripts
└── tsconfig.json                     # TypeScript configuration
```

---

## 🔌 Backend Integration

### API Configuration

The frontend connects to the backend via the `environment.ts` file:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'  // Backend API URL
};
```

**Important:** API keys should NEVER be in the frontend. All authentication is handled by the backend.

### API Endpoints Used

| Component | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| **Auth** | `/api/auth/login` | POST | User login |
| **Auth** | `/api/auth/me` | GET | Get current user |
| **User** | `/api/user/preferences` | POST | Update language/country |
| **Chat** | `/api/query/answer` | POST | Get AI answers to questions |
| **Chat** | `/api/query/search` | POST | Search documents without LLM |
| **Upload** | `/api/ingest/file` | POST | Upload PDF/text files |
| **Upload** | `/api/ingest/image` | POST | Upload images (OCR + parsing) |
| **Documents** | `/api/documents` | GET | List all documents |
| **Documents** | `/api/documents/{id}` | DELETE | Delete a document |
| **Lawyers** | `/api/lawyers` | GET | Get lawyer/paralegal list |
| **Analytics** | `/api/analytics/summary` | GET | Get analytics data |
| **Analytics** | `/api/analytics/feedback` | POST | Submit user feedback |

---

## 🧩 Components Overview

### 1. Chat Component (`/chat`)

**Location:** `src/app/components/chat/chat.component.ts`

**Features:**
- ChatGPT-style chat interface
- Real-time question answering
- Source citations with page numbers
- Message history
- Feedback buttons (thumbs up/down)

**Key Methods:**
- `sendMessage()` - Sends question to backend
- `formatMessage()` - Formats markdown in responses
- `submitFeedback()` - Submits user feedback

**API Integration:**
```typescript
this.chatService.askQuestion({ question: "..." })
  .subscribe(response => {
    // Handle answer and sources
  });
```

### 2. Upload Component (`/upload`)

**Location:** `src/app/components/upload/upload.component.ts`

**Features:**
- Drag-and-drop file upload
- Support for PDF, TXT, JPG, PNG files
- Progress tracking
- Organization and subject metadata
- Automatic OCR for images

**Key Methods:**
- `onFileSelected()` - Handles file selection
- `uploadFile()` - Uploads file to backend
- `formatFileSize()` - Formats file size display

**API Integration:**
```typescript
// For PDF/text files
POST /api/ingest/file

// For images
POST /api/ingest/image
```

### 3. Documents Component (`/documents`)

**Location:** `src/app/components/documents/documents.component.ts`

**Features:**
- Document library table
- Filter by organization, subject, type
- View document metadata
- Delete documents
- Chunk count display

**Key Methods:**
- `loadDocuments()` - Fetches document list
- `deleteDocument()` - Removes a document
- `getTypeIcon()` - Returns icon for file type

**API Integration:**
```typescript
GET /api/documents?organization=...&subject=...
DELETE /api/documents/{docId}
```

### 4. Analytics Component (`/analytics`)

**Location:** `src/app/components/analytics/analytics.component.ts`

**Features:**
- User statistics dashboard
- Query analytics
- Feedback metrics
- Top cited documents
- Confidence distribution charts

**Key Methods:**
- `loadAnalytics()` - Fetches analytics data
- `createCharts()` - Creates Chart.js visualizations
- `getTotalUsers()` - Calculates user totals

**API Integration:**
```typescript
GET /api/analytics/summary
```

---

## 🎨 Styling & UI Framework

### Angular Material
The app uses **Angular Material** for UI components:
- Material Design components
- Pre-built theme (indigo-pink)
- Responsive layout
- Accessible by default

### PrimeNG (Optional)
PrimeNG is included but not actively used. You can add PrimeNG components if needed.

### Custom Styles
Global styles are in `src/styles.scss`. Component-specific styles are inline in each component using the `styles` property.

---

## 🔧 Making Changes

### Adding a New Component

```bash
ng generate component components/my-new-component
```

Or manually create:
1. Create folder: `src/app/components/my-new-component/`
2. Create component file: `my-new-component.component.ts`
3. Add route in `app.routes.ts`:
```typescript
{
  path: 'my-route',
  loadComponent: () => import('./components/my-new-component/my-new-component.component')
    .then(m => m.MyNewComponent)
}
```

### Modifying API Calls

Edit `src/app/services/chat.service.ts` to add new API methods:

```typescript
newMethod(params: any): Observable<any> {
  return this.http.post(`${this.apiUrl}/api/new-endpoint`, params);
}
```

### Changing Backend URL

Edit `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://your-backend-url:8000'
};
```

For production, create `environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com'
};
```

### Adding New Routes

Edit `src/app/app.routes.ts`:
```typescript
{
  path: 'new-page',
  loadComponent: () => import('./components/new-page/new-page.component')
    .then(m => m.NewPageComponent)
}
```

Add navigation link in `app.component.ts` template.

---

## 📡 Service Layer

### ChatService (`src/app/services/chat.service.ts`)

Centralized service for all backend API calls.

**Methods:**
- `askQuestion(request: QueryRequest)` - Get AI answer
- `searchDocuments(query: string, top_k: number)` - Search without LLM
- `submitFeedback(isPositive: boolean)` - Submit feedback

**Usage:**
```typescript
constructor(private chatService: ChatService) {}

this.chatService.askQuestion({ question: "..." })
  .subscribe({
    next: (response) => {
      // Handle success
    },
    error: (error) => {
      // Handle error
    }
  });
```

---

## 🎯 Key Features

### 1. Real-time Chat
- Streaming responses (can be added)
- Message history
- Source citations
- Markdown formatting

### 2. Document Management
- Upload multiple file types
- Metadata tagging
- Document library
- Delete functionality

### 3. Analytics Dashboard
- User metrics
- Query statistics
- Feedback analysis
- Visual charts

### 4. Responsive Design
- Mobile-friendly
- Tablet support
- Desktop optimized
- Material Design

---

## 🛠️ Development Tips

### Hot Reload
The dev server automatically reloads on file changes. No need to restart.

### TypeScript Errors
Run `ng build` to check for TypeScript errors:
```bash
ng build
```

### Linting
Angular CLI includes ESLint. Check for issues:
```bash
ng lint
```

### Testing
Run unit tests:
```bash
ng test
```

### Debugging
1. Open browser DevTools (F12)
2. Check Network tab for API calls
3. Check Console for errors
4. Use Angular DevTools extension

---

## 🔐 Security Notes

### ⚠️ Important Security Practices

1. **Never put API keys in frontend code**
   - All API keys should be in the backend
   - Frontend only calls backend APIs

2. **CORS Configuration**
   - Backend must allow frontend origin
   - Configured in `backend/app/main.py`

3. **Input Validation**
   - Validate user inputs before sending to API
   - Sanitize displayed content

4. **Error Handling**
   - Don't expose sensitive error details
   - Show user-friendly error messages

---

## 📦 Dependencies

### Core Dependencies
- `@angular/core` - Angular framework
- `@angular/material` - Material Design components
- `rxjs` - Reactive programming
- `chart.js` - Charts and graphs

### Development Dependencies
- `@angular/cli` - Angular CLI
- `typescript` - TypeScript compiler
- `@angular-devkit/build-angular` - Build tools

See `package.json` for complete list.

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Deploy Options

1. **Static Hosting** (Netlify, Vercel, GitHub Pages)
   - Upload `dist/weknowrights-ca/` folder
   - Configure redirects for Angular routing

2. **Docker**
   ```dockerfile
   FROM nginx:alpine
   COPY dist/weknowrights-ca /usr/share/nginx/html
   ```

3. **Apache/Nginx**
   - Serve `dist/weknowrights-ca/` as static files
   - Configure URL rewriting for Angular routes

### Environment Variables

For production, update `environment.prod.ts` with production API URL.

---

## 🐛 Troubleshooting

### Backend Connection Issues

**Problem:** "Cannot connect to backend"

**Solutions:**
1. Check backend is running: `http://localhost:8000/health`
2. Verify `environment.ts` has correct API URL
3. Check CORS settings in backend
4. Check browser console for errors

### Build Errors

**Problem:** TypeScript compilation errors

**Solutions:**
1. Run `npm install` to ensure dependencies are installed
2. Check TypeScript version compatibility
3. Clear `.angular` cache: `rm -rf .angular`
4. Reinstall: `rm -rf node_modules && npm install`

### Module Not Found

**Problem:** "Cannot find module"

**Solutions:**
1. Check import paths are correct
2. Ensure component is exported
3. Verify route lazy loading syntax
4. Check `tsconfig.json` paths

### Styling Issues

**Problem:** Styles not applying

**Solutions:
1. Check Angular Material theme is imported
2. Verify component styles are in `styles` array
3. Check for CSS specificity conflicts
4. Use browser DevTools to inspect elements

---

## 📚 Additional Resources

- [Angular Documentation](https://angular.io/docs)
- [Angular Material](https://material.angular.io/)
- [RxJS Documentation](https://rxjs.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## 🎨 Customization Guide

### Changing Colors

Edit `src/styles.scss`:
```scss
$primary-color: #667eea;
$secondary-color: #764ba2;
```

Or modify Material theme in `angular.json`.

### Adding New Pages

1. Generate component: `ng generate component components/new-page`
2. Add route in `app.routes.ts`
3. Add navigation link in `app.component.ts`

### Modifying Chat Interface

Edit `src/app/components/chat/chat.component.ts`:
- Modify template for UI changes
- Update styles for visual changes
- Change `sendMessage()` for behavior changes

### Custom API Integration

Add methods to `chat.service.ts`:
```typescript
customMethod(data: any): Observable<any> {
  return this.http.post(`${this.apiUrl}/api/custom`, data);
}
```

---

## 📝 Code Style

- Use TypeScript strict mode
- Follow Angular style guide
- Use async/await or RxJS observables
- Component-based architecture
- Standalone components (no NgModules)

---

## 🤝 Contributing

When making changes:

1. Test locally with `ng serve`
2. Check TypeScript compilation: `ng build`
3. Verify API integration works
4. Test on different screen sizes
5. Check browser console for errors

---

## 📞 Support

For issues or questions:
- Check backend logs
- Review browser console
- Verify API endpoints
- Check network requests in DevTools

---

**Happy Coding! 🚀**
