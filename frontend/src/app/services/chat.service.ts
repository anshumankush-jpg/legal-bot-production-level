import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserContextService } from './user-context.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: any[];
  structuredData?: {
    demeritPoints?: string;
    consequences?: string[];
    option1?: string;
    option2?: string;
  };
}

export interface ChatRequest {
  message: string;
  language: string;
  country: string;
  province: string;
  offenceNumber?: string;
  contextDocIds?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(
    private http: HttpClient,
    private userContext: UserContextService
  ) {}

  sendMessage(question: string): Observable<any> {
    const preferences = this.userContext.getPreferences();
    if (!preferences) {
      throw new Error('User preferences not set');
    }

    const request: ChatRequest = {
      message: question,
      language: preferences.language,
      country: preferences.country,
      province: preferences.provinceOrState,
      offenceNumber: preferences.offenceNumber,
      contextDocIds: this.userContext.getRecentDocIds()
    };

    return this.http.post(`${this.apiUrl}/artillery/chat`, request);
  }

  askQuestion(request: { question: string; offence_number?: string }): Observable<any> {
    const preferences = this.userContext.getPreferences();
    const chatRequest = {
      message: request.question,
      offence_number: request.offence_number || preferences?.offenceNumber,
      top_k: 5
    };

    return this.http.post(`${this.apiUrl}/artillery/chat`, chatRequest);
  }

  submitFeedback(isPositive: boolean): Observable<any> {
    return this.http.post(`${this.apiUrl}/analytics/feedback`, null, {
      params: {
        is_positive: isPositive.toString()
      }
    });
  }
}

