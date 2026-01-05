import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface UserPreferences {
  language: string;
  country: string;
  provinceOrState: string;
  offenceNumber?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserContextService {
  private preferencesSubject = new BehaviorSubject<UserPreferences | null>(null);
  public preferences$ = this.preferencesSubject.asObservable();

  private recentDocIdsSubject = new BehaviorSubject<string[]>([]);
  public recentDocIds$ = this.recentDocIdsSubject.asObservable();

  private sessionIdSubject = new BehaviorSubject<string | null>(null);
  public sessionId$ = this.sessionIdSubject.asObservable();

  constructor() {
    this.loadFromStorage();
  }

  setPreferences(prefs: UserPreferences): void {
    this.preferencesSubject.next(prefs);
    localStorage.setItem('userPreferences', JSON.stringify(prefs));
  }

  getPreferences(): UserPreferences | null {
    return this.preferencesSubject.value;
  }

  addRecentDocId(docId: string): void {
    const current = this.recentDocIdsSubject.value;
    if (!current.includes(docId)) {
      const updated = [...current, docId];
      this.recentDocIdsSubject.next(updated);
      localStorage.setItem('recentDocIds', JSON.stringify(updated));
    }
  }

  getRecentDocIds(): string[] {
    return this.recentDocIdsSubject.value;
  }

  setSessionId(sessionId: string): void {
    this.sessionIdSubject.next(sessionId);
    localStorage.setItem('sessionId', sessionId);
  }

  isSetupComplete(): boolean {
    const prefs = this.getPreferences();
    return !!(prefs?.language && prefs?.country && prefs?.provinceOrState);
  }

  private loadFromStorage(): void {
    const stored = localStorage.getItem('userPreferences');
    if (stored) {
      try {
        this.preferencesSubject.next(JSON.parse(stored));
      } catch (e) {
        console.error('Error loading preferences:', e);
      }
    }

    const storedDocs = localStorage.getItem('recentDocIds');
    if (storedDocs) {
      try {
        this.recentDocIdsSubject.next(JSON.parse(storedDocs));
      } catch (e) {
        console.error('Error loading recent docs:', e);
      }
    }

    const storedSession = localStorage.getItem('sessionId');
    if (storedSession) {
      this.sessionIdSubject.next(storedSession);
    }
  }

  clear(): void {
    this.preferencesSubject.next(null);
    this.recentDocIdsSubject.next([]);
    this.sessionIdSubject.next(null);
    localStorage.removeItem('userPreferences');
    localStorage.removeItem('recentDocIds');
    localStorage.removeItem('sessionId');
  }
}