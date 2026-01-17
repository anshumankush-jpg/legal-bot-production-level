import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../environments/environment';

export const apiInterceptor: HttpInterceptorFn = (req, next) => {
  // Get base API URL from environment
  const apiUrl = environment.apiUrl || 'http://localhost:8000';

  // If request is already absolute, use it as-is
  // Otherwise, prepend the API URL
  let url = req.url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    // Remove leading slash if present to avoid double slashes
    const path = url.startsWith('/') ? url.substring(1) : url;
    url = `${apiUrl}/${path}`;
  }

  // Clone request with new URL
  const clonedReq = req.clone({
    url: url,
    setHeaders: {
      'Content-Type': 'application/json',
      // Add auth token if available
      ...(getAuthToken() ? { 'Authorization': `Bearer ${getAuthToken()}` } : {}),
      // Add dev user ID header for local development (if not in production)
      ...(getDevUserId() ? { 'x-dev-user-id': getDevUserId() } : {})
    }
  });

  return next(clonedReq);
};

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token') || localStorage.getItem('authToken');
}

/**
 * Get dev user ID for local development
 * In production, this should be removed and proper auth should be used
 */
function getDevUserId(): string | null {
  if (environment.production) return null;
  if (typeof window === 'undefined') return null;
  
  // Check if user is logged in (has token)
  const token = getAuthToken();
  if (token) return null; // Don't use dev header if user is authenticated
  
  // Return dev user ID from localStorage or use default
  return localStorage.getItem('dev_user_id') || 'dev-user-001';
}
