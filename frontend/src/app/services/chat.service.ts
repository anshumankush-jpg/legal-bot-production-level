import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { AuthService } from './auth.service';

export interface Conversation {
  conversation_id: string;
  user_id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  message_count?: number;
  preview?: string;
}

export interface Message {
  message_id: string;
  conversation_id: string;
  user_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  attachments?: any[];
  created_at: Date;
  metadata?: any;
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
  conversation_history?: Message[];
  law_category?: string;
  jurisdiction?: string;
  language?: string;
}

export interface ChatResponse {
  message_id: string;
  answer: string;
  citations?: any[];
  chunks_used?: number;
  confidence?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000';
  
  private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
  private activeConversationSubject = new BehaviorSubject<string | null>(null);
  private messagesSubject = new BehaviorSubject<Message[]>([]);

  public conversations$ = this.conversationsSubject.asObservable();
  public activeConversation$ = this.activeConversationSubject.asObservable();
  public messages$ = this.messagesSubject.asObservable();

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    // Load conversations when user logs in
    this.authService.isAuthenticated$.subscribe(isAuth => {
      if (isAuth) {
        this.loadConversations();
      } else {
        this.conversationsSubject.next([]);
        this.messagesSubject.next([]);
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

  // ========================================
  // CONVERSATION MANAGEMENT
  // ========================================

  loadConversations(): void {
    this.http.get<Conversation[]>(`${this.apiUrl}/conversations`, {
      headers: this.getHeaders()
    }).subscribe({
      next: (conversations) => {
        this.conversationsSubject.next(conversations);
      },
      error: (error) => {
        console.error('Failed to load conversations:', error);
      }
    });
  }

  createConversation(title: string = 'New Chat'): Observable<Conversation> {
    return this.http.post<Conversation>(`${this.apiUrl}/conversations`, {
      title
    }, {
      headers: this.getHeaders()
    }).pipe(
      tap(conversation => {
        const current = this.conversationsSubject.value;
        this.conversationsSubject.next([conversation, ...current]);
        this.activeConversationSubject.next(conversation.conversation_id);
      })
    );
  }

  renameConversation(conversationId: string, newTitle: string): Observable<Conversation> {
    return this.http.patch<Conversation>(`${this.apiUrl}/conversations/${conversationId}`, {
      title: newTitle
    }, {
      headers: this.getHeaders()
    }).pipe(
      tap(updated => {
        const current = this.conversationsSubject.value;
        const index = current.findIndex(c => c.conversation_id === conversationId);
        if (index !== -1) {
          current[index] = updated;
          this.conversationsSubject.next([...current]);
        }
      })
    );
  }

  deleteConversation(conversationId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/conversations/${conversationId}`, {
      headers: this.getHeaders()
    }).pipe(
      tap(() => {
        const current = this.conversationsSubject.value;
        this.conversationsSubject.next(current.filter(c => c.conversation_id !== conversationId));
        
        if (this.activeConversationSubject.value === conversationId) {
          this.activeConversationSubject.next(null);
          this.messagesSubject.next([]);
        }
      })
    );
  }

  setActiveConversation(conversationId: string): void {
    this.activeConversationSubject.next(conversationId);
    this.loadMessages(conversationId);
  }

  getActiveConversationId(): string | null {
    return this.activeConversationSubject.value;
  }

  searchConversations(query: string): Conversation[] {
    const current = this.conversationsSubject.value;
    if (!query.trim()) return current;

    const lowerQuery = query.toLowerCase();
    return current.filter(conv => 
      conv.title.toLowerCase().includes(lowerQuery) ||
      conv.preview?.toLowerCase().includes(lowerQuery)
    );
  }

  // ========================================
  // MESSAGE MANAGEMENT
  // ========================================

  loadMessages(conversationId: string): void {
    this.http.get<Message[]>(`${this.apiUrl}/messages`, {
      headers: this.getHeaders(),
      params: { conversationId }
    }).subscribe({
      next: (messages) => {
        this.messagesSubject.next(messages);
      },
      error: (error) => {
        console.error('Failed to load messages:', error);
        this.messagesSubject.next([]);
      }
    });
  }

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/api/artillery/chat`, request, {
      headers: this.getHeaders()
    }).pipe(
      tap(response => {
        // Add user message
        const userMessage: Message = {
          message_id: crypto.randomUUID(),
          conversation_id: request.conversation_id,
          user_id: this.authService.getCurrentUser()?.user_id || '',
          role: 'user',
          content: request.message,
          created_at: new Date()
        };

        // Add assistant message
        const assistantMessage: Message = {
          message_id: response.message_id,
          conversation_id: request.conversation_id,
          user_id: this.authService.getCurrentUser()?.user_id || '',
          role: 'assistant',
          content: response.answer,
          created_at: new Date(),
          metadata: {
            citations: response.citations,
            chunks_used: response.chunks_used,
            confidence: response.confidence
          }
        };

        const current = this.messagesSubject.value;
        this.messagesSubject.next([...current, userMessage, assistantMessage]);

        // Update conversation's updated_at
        this.updateConversationTimestamp(request.conversation_id);
      })
    );
  }

  private updateConversationTimestamp(conversationId: string): void {
    const current = this.conversationsSubject.value;
    const index = current.findIndex(c => c.conversation_id === conversationId);
    if (index !== -1) {
      current[index].updated_at = new Date();
      // Move to top
      const conv = current.splice(index, 1)[0];
      this.conversationsSubject.next([conv, ...current]);
    }
  }

  getMessages(): Message[] {
    return this.messagesSubject.value;
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }
}
