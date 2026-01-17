import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';

export interface User {
  user_id: string;
  email: string;
  display_name: string;
  role: 'client' | 'lawyer' | 'admin';
  created_at: Date;
  last_login_at: Date;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(null);

  public currentUser$ = this.currentUserSubject.asObservable();
  public token$ = this.tokenSubject.asObservable();
  public isAuthenticated$ = new BehaviorSubject<boolean>(false);

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const token = localStorage.getItem('legid_token');
    const userJson = localStorage.getItem('legid_user');

    if (token && userJson) {
      try {
        const user = JSON.parse(userJson);
        this.tokenSubject.next(token);
        this.currentUserSubject.next(user);
        this.isAuthenticated$.next(true);
      } catch (e) {
        this.logout();
      }
    }
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/login`, {
      email,
      password
    }).pipe(
      tap(response => this.handleAuthSuccess(response))
    );
  }

  loginWithGoogle(): void {
    // Initiate Google OAuth flow
    this.http.get<{auth_url: string, state: string}>(`${this.apiUrl}/api/auth/google/login`)
      .subscribe({
        next: (response) => {
          // Store state for CSRF protection
          sessionStorage.setItem('oauth_state', response.state);
          // Redirect to Google auth
          window.location.href = response.auth_url;
        },
        error: (error) => {
          console.error('Google OAuth initiation failed:', error);
        }
      });
  }

  loginWithMicrosoft(): void {
    // Initiate Microsoft OAuth flow
    this.http.get<{auth_url: string, state: string}>(`${this.apiUrl}/api/auth/microsoft/login`)
      .subscribe({
        next: (response) => {
          // Store state for CSRF protection
          sessionStorage.setItem('oauth_state', response.state);
          // Redirect to Microsoft auth
          window.location.href = response.auth_url;
        },
        error: (error) => {
          console.error('Microsoft OAuth initiation failed:', error);
        }
      });
  }

  signup(email: string, password: string, name?: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/signup`, {
      email,
      password,
      name
    }).pipe(
      tap(response => this.handleAuthSuccess(response))
    );
  }

  private handleAuthSuccess(response: AuthResponse): void {
    localStorage.setItem('legid_token', response.access_token);
    localStorage.setItem('legid_user', JSON.stringify(response.user));
    
    if (response.refresh_token) {
      localStorage.setItem('legid_refresh_token', response.refresh_token);
    }

    this.tokenSubject.next(response.access_token);
    this.currentUserSubject.next(response.user);
    this.isAuthenticated$.next(true);
  }

  logout(): void {
    localStorage.removeItem('legid_token');
    localStorage.removeItem('legid_user');
    localStorage.removeItem('legid_refresh_token');

    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
    this.isAuthenticated$.next(false);

    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return this.tokenSubject.value;
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.isAuthenticated$.value;
  }

  refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem('legid_refresh_token');
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      tap(response => this.handleAuthSuccess(response))
    );
  }

  getCurrentUserFromAPI(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/auth/me`).pipe(
      tap(user => {
        this.currentUserSubject.next(user as User);
        this.isAuthenticated$.next(true);
        localStorage.setItem('legid_user', JSON.stringify(user));
      })
    );
  }

  logoutAPI(): Observable<any> {
    const refreshToken = localStorage.getItem('legid_refresh_token');
    return this.http.post(`${this.apiUrl}/api/auth/logout`, {
      refresh_token: refreshToken
    }).pipe(
      tap(() => {
        this.logout();
      })
    );
  }
}
