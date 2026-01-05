# Angular Frontend - Complete Implementation Guide

## ✅ Implementation Status

All Angular components, services, guards, and routes have been created:

### Components Created
1. **Login Component** (`pages/login/`)
   - Email/password authentication
   - Form validation
   - Error handling

2. **Setup Wizard Component** (`pages/setup/`)
   - 5-step onboarding flow
   - Language selection
   - Country selection
   - Province/State selection with search
   - Offence number (optional)
   - Confirmation screen

3. **Chat Component** (`pages/chat/`)
   - Document upload (PDF, DOCX, TXT)
   - Image upload with camera support
   - Real-time chat with Artillery backend
   - Progress indicators
   - Citation display
   - System messages

4. **Profile Component** (`pages/profile/`)
   - View user preferences
   - Edit preferences
   - Logout

### Services Created
- `AuthService` - Authentication management
- `UserContextService` - User preferences and context
- `UserPreferencesService` - Preferences API integration
- `UploadService` - File/image upload with progress
- `ChatService` - Updated for Artillery endpoints

### Guards Created
- `AuthGuard` - Protects routes requiring authentication
- `SetupGuard` - Ensures setup is complete before chat

### Routes Configured
```
/ → /login
/login → LoginComponent
/setup → SetupWizardComponent (AuthGuard)
/chat → ChatComponent (AuthGuard + SetupGuard)
/profile → ProfileComponent (AuthGuard)
```

## 🚀 Setup Instructions

### Option 1: Use Angular CLI (Recommended)

1. **Install Angular CLI globally** (if not already installed):
   ```bash
   npm install -g @angular/cli
   ```

2. **Create new Angular project** (if starting fresh):
   ```bash
   ng new plaza-ai-frontend --routing --style=scss --standalone
   cd plaza-ai-frontend
   ```

3. **Copy all created files** to the new project:
   - Copy `src/app/pages/` → `src/app/pages/`
   - Copy `src/app/guards/` → `src/app/guards/`
   - Copy `src/app/services/` → `src/app/services/`
   - Copy `src/styles/_design-tokens-compat.scss` → `src/styles/`

4. **Install dependencies**:
   ```bash
   npm install @angular/common @angular/router @angular/forms @angular/platform-browser @angular/platform-browser-dynamic
   ```

5. **Update `angular.json`** to include SCSS:
   ```json
   {
     "projects": {
       "plaza-ai-frontend": {
         "architect": {
           "build": {
             "options": {
               "stylePreprocessorOptions": {
                 "includePaths": ["src/styles"]
               }
             }
           }
         }
       }
     }
   }
   ```

6. **Start development server**:
   ```bash
   ng serve
   ```

### Option 2: Use Vite with Angular Plugin

1. **Install Angular Vite plugin**:
   ```bash
   npm install @analogjs/vite-plugin-angular --save-dev
   ```

2. **Update `vite.config.js`**:
   ```javascript
   import { defineConfig } from 'vite';
   import angular from '@analogjs/vite-plugin-angular';

   export default defineConfig({
     plugins: [angular()],
     server: {
       port: 4200,
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true
         }
       }
     }
   });
   ```

3. **Update `package.json`**:
   ```json
   {
     "dependencies": {
       "@angular/core": "^17.0.0",
       "@angular/common": "^17.0.0",
       "@angular/router": "^17.0.0",
       "@angular/forms": "^17.0.0",
       "@angular/platform-browser": "^17.0.0",
       "@angular/platform-browser-dynamic": "^17.0.0"
     },
     "devDependencies": {
       "@analogjs/vite-plugin-angular": "^1.0.0",
       "typescript": "^5.0.0"
     }
   }
   ```

4. **Create `index.html`**:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>PLAZA-AI Legal Assistant</title>
   </head>
   <body>
     <app-root></app-root>
     <script type="module" src="/src/main.ts"></script>
   </body>
   </html>
   ```

5. **Start development server**:
   ```bash
   npm start
   ```

## 📋 Configuration Checklist

### 1. Update `app.component.ts`
Ensure it uses RouterOutlet:
```typescript
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  template: '<router-outlet></router-outlet>'
})
```

### 2. Update `app.routes.ts`
Routes are already configured with guards.

### 3. Environment Configuration
Create `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

### 4. HTTP Client Configuration
Ensure `provideHttpClient()` is in `main.ts` (already added).

## 🧪 Testing the Application

### 1. Start Backend
```bash
python start_local_server.py
```

### 2. Start Frontend
```bash
cd frontend
npm start
# or
ng serve
```

### 3. Test Flow
1. Navigate to `http://localhost:4200` (or configured port)
2. Should redirect to `/login`
3. Login (or skip if auth not implemented yet)
4. Complete setup wizard (5 steps)
5. Access chat interface
6. Upload document and test chat

## 🎨 Design System

All components use design tokens from `_design-tokens-compat.scss`:
- Primary Navy: `$color-navy` (#0B1F3B)
- Accent Teal: `$color-teal` (#00BCD4)
- Professional legal-tech theme
- Responsive design
- Mobile-friendly

## 📝 Notes

- All components are **standalone** (Angular 17+ style)
- Uses **reactive forms** for form handling
- **TypeScript** throughout
- **SCSS** for styling with design tokens
- **RxJS** for reactive programming
- **LocalStorage** for persistence
- **Error handling** throughout
- **Loading states** for async operations
- **Progress indicators** for uploads

## 🔧 Troubleshooting

### Issue: Module not found errors
**Solution**: Ensure all Angular dependencies are installed:
```bash
npm install @angular/core @angular/common @angular/router @angular/forms
```

### Issue: SCSS import errors
**Solution**: Add style preprocessor options to `angular.json` or configure in `vite.config.js`

### Issue: Routes not working
**Solution**: Ensure `provideRouter(routes)` is in `main.ts` providers

### Issue: HTTP requests failing
**Solution**: 
1. Ensure `provideHttpClient()` is in `main.ts`
2. Check CORS configuration on backend
3. Verify API URL in services

## ✅ Completion Status

- ✅ All components created
- ✅ All services implemented
- ✅ Guards configured
- ✅ Routes set up
- ✅ Design tokens integrated
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Upload functionality
- ✅ Chat integration

**The Angular frontend is complete and ready for testing!** 🎉