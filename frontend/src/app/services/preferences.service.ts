import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { AuthService } from './auth.service';

export interface UserPreferences {
  user_id: string;
  theme: 'dark' | 'light';
  font_size: 'small' | 'medium' | 'large';
  response_style: 'concise' | 'detailed' | 'legal';
  language: string;
  auto_read_responses: boolean;
  law_category?: string;
  jurisdiction?: string;
  province?: string;
  country?: string;
}

const DEFAULT_PREFERENCES: Partial<UserPreferences> = {
  theme: 'dark',
  font_size: 'medium',
  response_style: 'detailed',
  language: 'en',
  auto_read_responses: false,
  country: 'CA'
};

@Injectable({
  providedIn: 'root'
})
export class PreferencesService {
  private apiUrl = 'http://localhost:8000';
  
  private preferencesSubject = new BehaviorSubject<UserPreferences | null>(null);
  public preferences$ = this.preferencesSubject.asObservable();

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    // Load preferences when user logs in
    this.authService.isAuthenticated$.subscribe(isAuth => {
      if (isAuth) {
        this.loadPreferences();
      } else {
        this.preferencesSubject.next(null);
      }
    });
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  loadPreferences(): void {
    this.http.get<UserPreferences>(`${this.apiUrl}/preferences`, {
      headers: this.getHeaders()
    }).subscribe({
      next: (prefs) => {
        this.preferencesSubject.next(prefs);
      },
      error: (error) => {
        console.error('Failed to load preferences:', error);
        // Use defaults if can't load
        const user = this.authService.getCurrentUser();
        if (user) {
          this.preferencesSubject.next({
            ...DEFAULT_PREFERENCES,
            user_id: user.user_id
          } as UserPreferences);
        }
      }
    });
  }

  updatePreferences(updates: Partial<UserPreferences>): Observable<UserPreferences> {
    return this.http.put<UserPreferences>(`${this.apiUrl}/preferences`, updates, {
      headers: this.getHeaders()
    }).pipe(
      tap(updated => {
        this.preferencesSubject.next(updated);
      })
    );
  }

  getPreferences(): UserPreferences | null {
    return this.preferencesSubject.value;
  }

  setLanguage(language: string): void {
    const current = this.preferencesSubject.value;
    if (current) {
      this.updatePreferences({ language }).subscribe();
    }
  }

  setResponseStyle(style: 'concise' | 'detailed' | 'legal'): void {
    const current = this.preferencesSubject.value;
    if (current) {
      this.updatePreferences({ response_style: style }).subscribe();
    }
  }

  setTheme(theme: 'dark' | 'light'): void {
    const current = this.preferencesSubject.value;
    if (current) {
      this.updatePreferences({ theme }).subscribe();
    }
  }
}
