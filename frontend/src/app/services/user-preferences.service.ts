import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserPreferences } from './user-context.service';

@Injectable({
  providedIn: 'root'
})
export class UserPreferencesService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  savePreferences(preferences: UserPreferences): Observable<any> {
    return this.http.post(`${this.apiUrl}/user/preferences`, preferences);
  }
}