import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatMessage } from '../../services/chat.service';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="chat-wrapper">
      <!-- ChatGPT-style Welcome Screen -->
      <div *ngIf="messages.length === 0 && !isLoading" class="welcome-screen">
        <div class="welcome-content">
          <h1 class="welcome-title">What can I help with?</h1>
          <div class="quick-actions">
            <button class="quick-action-btn" (click)="setQuickQuestion('What are my options for a traffic ticket?')">
              <mat-icon>traffic</mat-icon>
              <span>Traffic Tickets</span>
            </button>
            <button class="quick-action-btn" (click)="setQuickQuestion('How do I dispute a ticket?')">
              <mat-icon>gavel</mat-icon>
              <span>Dispute Process</span>
            </button>
            <button class="quick-action-btn" (click)="setQuickQuestion('What are demerit points?')">
              <mat-icon>info</mat-icon>
              <span>Demerit Points</span>
            </button>
            <button class="quick-action-btn" (click)="setQuickQuestion('What happens if I pay a ticket?')">
              <mat-icon>payment</mat-icon>
              <span>Payment Options</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="messages-container" #messagesContainer>
        <div *ngFor="let message of messages" class="message-row" [ngClass]="message.role">
          <div class="message-wrapper">
            <div class="avatar">
              <mat-icon *ngIf="message.role === 'user'">person</mat-icon>
              <div *ngIf="message.role === 'assistant'" class="ai-avatar">AI</div>
            </div>
            <div class="message-bubble">
              <div class="message-text" [innerHTML]="formatMessage(message.content)"></div>
              
              <!-- Sources (collapsible) -->
              <div *ngIf="message.sources && message.sources.length > 0" class="sources-section">
                <button class="sources-toggle" (click)="toggleSources(message)">
                  <mat-icon>{{ message.showSources ? 'expand_less' : 'expand_more' }}</mat-icon>
                  <span>Sources ({{ message.sources.length }})</span>
                </button>
                <div *ngIf="message.showSources" class="sources-list">
                  <div *ngFor="let source of message.sources" class="source-item">
                    <strong>{{ source.source }}</strong>
                    <span *ngIf="source.page"> - Page {{ source.page }}</span>
                    <p class="source-snippet">{{ source.snippet }}</p>
                  </div>
                </div>
              </div>

              <!-- Message Actions -->
              <div *ngIf="message.role === 'assistant'" class="message-actions">
                <button class="action-btn" (click)="copyMessage(message)" title="Copy">
                  <mat-icon>content_copy</mat-icon>
                </button>
                <button class="action-btn" (click)="submitFeedback(true, message)" title="Helpful">
                  <mat-icon>thumb_up</mat-icon>
                </button>
                <button class="action-btn" (click)="submitFeedback(false, message)" title="Not helpful">
                  <mat-icon>thumb_down</mat-icon>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading Indicator -->
        <div *ngIf="isLoading" class="message-row assistant">
          <div class="message-wrapper">
            <div class="avatar">
              <div class="ai-avatar">AI</div>
            </div>
            <div class="message-bubble">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ChatGPT-style Input Area -->
      <div class="input-area">
        <div class="input-wrapper">
          <div class="input-container">
            <textarea
              #messageInput
              [(ngModel)]="currentQuestion"
              (keydown.enter)="onEnterKey($event)"
              (input)="adjustTextareaHeight()"
              [disabled]="isLoading"
              placeholder="Ask anything about your legal documents..."
              class="chat-input"
              rows="1"
            ></textarea>
            <input
              #fileInput
              type="file"
              (change)="onFileSelected($event)"
              accept=".pdf,.docx,.doc,.txt,.csv,.png,.jpg,.jpeg"
              style="display: none;"
            />
            <button
              class="upload-btn"
              (click)="uploadFile()"
              [disabled]="isLoading"
              title="Upload document"
              type="button"
            >
              <mat-icon>add</mat-icon>
            </button>
            <button
              class="send-btn"
              (click)="sendMessage()"
              [disabled]="!currentQuestion.trim() || isLoading"
              [class.sending]="isLoading"
            >
              <mat-icon *ngIf="!isLoading">send</mat-icon>
              <mat-spinner *ngIf="isLoading" diameter="20"></mat-spinner>
            </button>
          </div>
          <p class="input-footer">
            This is general information only, not legal advice. For advice about your specific case, consult a licensed lawyer or paralegal.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-wrapper {
      display: flex;
      flex-direction: column;
      height: 100vh;
      background: #212121;
      position: relative;
      color: #ececec;
    }

    /* Welcome Screen - ChatGPT Style */
    .welcome-screen {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .welcome-content {
      text-align: center;
      max-width: 800px;
    }

    .welcome-title {
      font-size: 2.5rem;
      font-weight: 600;
      color: #ececec;
      margin-bottom: 2rem;
    }

    .quick-actions {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-top: 2rem;
    }

    .quick-action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 0.9rem;
      color: #ececec;
    }

    .quick-action-btn:hover {
      background: #3a3a3a;
      border-color: #00BCD4;
      transform: translateY(-2px);
    }

    .quick-action-btn mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: #00BCD4;
    }

    /* Messages Container */
    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 3rem 0;
      background: #212121;
    }

    .message-row {
      padding: 2rem 0;
      display: flex;
      justify-content: center;
    }

    .message-row.user {
      background: #1a1a1a;
    }

    .message-wrapper {
      display: flex;
      gap: 1.5rem;
      max-width: 900px;
      width: 100%;
      padding: 0 3rem;
    }

    .avatar {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #00BCD4;
      color: white;
    }

    .avatar mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .ai-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #0B1F3B;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .message-bubble {
      flex: 1;
      padding: 1.5rem 2rem;
      background: #2d2d2d;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      margin-left: 0.5rem;
    }

    .message-row.user .message-bubble {
      background: #00BCD4;
      color: white;
      margin-left: 0;
      margin-right: 0.5rem;
    }

    .message-text {
      line-height: 1.8;
      color: #ececec;
      white-space: pre-wrap;
      font-size: 1rem;
    }

    .message-row.user .message-text {
      color: white;
    }

    /* Sources */
    .sources-section {
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid #404040;
    }

    .sources-toggle {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: none;
      border: none;
      color: #999;
      cursor: pointer;
      font-size: 0.875rem;
      padding: 0.5rem 0;
      transition: color 0.2s;
    }

    .sources-toggle:hover {
      color: #00BCD4;
    }

    .sources-list {
      margin-top: 1rem;
    }

    .source-item {
      padding: 1rem;
      background: #1a1a1a;
      border-radius: 8px;
      margin-bottom: 0.75rem;
      font-size: 0.875rem;
      border: 1px solid #404040;
    }

    .source-item strong {
      color: #00BCD4;
    }

    .source-snippet {
      margin: 0.5rem 0 0 0;
      color: #999;
      font-style: italic;
    }

    /* Message Actions */
    .message-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid #404040;
    }

    .action-btn {
      background: none;
      border: none;
      color: #999;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 4px;
      display: flex;
      align-items: center;
      transition: all 0.2s;
    }

    .action-btn:hover {
      background: #3a3a3a;
      color: #00BCD4;
    }

    .action-btn mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    /* Typing Indicator */
    .typing-indicator {
      display: flex;
      gap: 4px;
      padding: 0.5rem 0;
    }

    .typing-indicator span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #00BCD4;
      animation: typing 1.4s infinite;
    }

    .typing-indicator span:nth-child(2) {
      animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes typing {
      0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
      30% { transform: translateY(-10px); opacity: 1; }
    }

    /* Input Area - ChatGPT Style Dark */
    .input-area {
      padding: 2rem 3rem;
      background: #212121;
      border-top: 1px solid #404040;
    }

    .input-wrapper {
      max-width: 900px;
      margin: 0 auto;
    }

    .input-container {
      display: flex;
      align-items: flex-end;
      gap: 0.5rem;
      padding: 1rem 1.5rem;
      background: #2d2d2d;
      border: 2px solid #404040;
      border-radius: 28px;
      transition: all 0.2s;
    }

    .input-container:focus-within {
      border-color: #00BCD4;
      background: #353535;
      box-shadow: 0 0 0 4px rgba(0, 188, 212, 0.15);
    }

    .chat-input {
      flex: 1;
      border: none;
      background: transparent;
      resize: none;
      font-size: 1rem;
      line-height: 1.6;
      max-height: 200px;
      overflow-y: auto;
      outline: none;
      font-family: inherit;
      color: #ececec;
    }

    .chat-input::placeholder {
      color: #666;
    }

    .upload-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: none;
      background: #4CAF50;
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      flex-shrink: 0;
      margin-right: 8px;
    }

    .upload-btn:hover:not(:disabled) {
      background: #388E3C;
      transform: scale(1.05);
    }

    .upload-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .upload-btn mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .send-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: none;
      background: #00BCD4;
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      flex-shrink: 0;
    }

    .send-btn:hover:not(:disabled) {
      background: #0097A7;
      transform: scale(1.05);
    }

    .send-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .send-btn mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .input-footer {
      margin-top: 1rem;
      text-align: center;
      font-size: 0.75rem;
      color: #666;
      padding: 0 1rem;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .welcome-title {
        font-size: 1.75rem;
      }

      .quick-actions {
        grid-template-columns: 1fr;
      }

      .message-wrapper {
        padding: 0 1rem;
      }

      .input-area {
        padding: 1rem;
      }
    }
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  messages: ChatMessage[] = [];
  currentQuestion: string = '';
  currentOffenceNumber: string = '';
  isLoading: boolean = false;
  isUploading: boolean = false;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    // Check backend connection on init
    this.checkBackendConnection();
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  checkBackendConnection(): void {
    // Verify backend is accessible
    fetch(`${environment.apiUrl}/health`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.log('✅ Backend connected:', data);
        if (data.status === 'unhealthy' && data.index_size === 0) {
          console.warn('⚠️ Backend is running but no documents indexed yet');
        }
      })
      .catch(err => {
        console.error('❌ Backend connection error:', err);
        console.error('Make sure backend is running on', environment.apiUrl);
      });
  }

  scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  setQuickQuestion(question: string): void {
    this.currentQuestion = question;
    this.sendMessage();
  }

  onEnterKey(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  adjustTextareaHeight(): void {
    const textarea = this.messageInput.nativeElement;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  }

  sendMessage(): void {
    if (!this.currentQuestion.trim() || this.isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: this.currentQuestion,
      timestamp: new Date()
    };

    this.messages.push(userMessage);
    const question = this.currentQuestion;
    this.currentQuestion = '';
    this.isLoading = true;

    // Reset textarea height
    if (this.messageInput) {
      this.messageInput.nativeElement.style.height = 'auto';
    }

    this.chatService.askQuestion({
      question,
      offence_number: this.currentOffenceNumber || undefined
    }).subscribe({
      next: (response) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.answer || 'I received your question but got an empty response.',
          sources: response.sources,
          timestamp: new Date(),
          showSources: false
        };
        this.messages.push(assistantMessage);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Chat error:', error);
        
        // Better error messages with troubleshooting
        let errorMessage = 'I apologize, but I encountered an error while processing your question.';
        let troubleshooting = '';
        
        if (error.status === 0 || error.name === 'HttpErrorResponse') {
          errorMessage = 'Unable to connect to the backend server.';
          troubleshooting = '\n\n**Troubleshooting:**\n- Make sure the backend is running: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`\n- Check that the server is accessible at http://localhost:8000\n- Verify CORS is configured correctly';
        } else if (error.status === 500) {
          errorMessage = 'The server encountered an error processing your request.';
          troubleshooting = '\n\n**Troubleshooting:**\n- Check backend logs for detailed error\n- Verify OpenAI API key is configured\n- Ensure documents are ingested';
        } else if (error.status === 404) {
          errorMessage = 'The API endpoint was not found.';
          troubleshooting = '\n\n**Troubleshooting:**\n- Verify backend routes are correct\n- Check API version compatibility';
        } else if (error.error?.detail) {
          errorMessage = `Error: ${error.error.detail}`;
          troubleshooting = '\n\nPlease check backend configuration and try again.';
        } else {
          troubleshooting = '\n\n**Please check:**\n- Backend server is running\n- Documents are ingested\n- API keys are configured\n- Network connection is stable';
        }
        
        const errorMsg: ChatMessage = {
          role: 'assistant',
          content: errorMessage + troubleshooting,
          timestamp: new Date()
        };
        this.messages.push(errorMsg);
        this.isLoading = false;
      }
    });
  }

  formatMessage(content: string): string {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  toggleSources(message: ChatMessage): void {
    message.showSources = !message.showSources;
  }

  copyMessage(message: ChatMessage): void {
    navigator.clipboard.writeText(message.content).then(() => {
      // Could show a toast notification here
      console.log('Message copied to clipboard');
    });
  }

  submitFeedback(isPositive: boolean, message: ChatMessage): void {
    this.chatService.submitFeedback(isPositive).subscribe({
      next: () => {
        console.log('Feedback submitted:', isPositive ? 'positive' : 'negative');
      },
      error: (error) => {
        console.error('Error submitting feedback:', error);
      }
    });
  }

  uploadFile(): void {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  onFileSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];

    if (file) {
      this.uploadDocument(file);
    }
  }

  uploadDocument(file: File): void {
    this.isUploading = true;

    const formData = new FormData();
    formData.append('file', file);

    // Add system message about upload starting
    const uploadMessage: ChatMessage = {
      role: 'assistant',
      content: `Uploading ${file.name}...`,
      timestamp: new Date(),
      isTemporary: true
    };
    this.messages.push(uploadMessage);

    fetch(`${environment.apiUrl}/api/rtld/documents/upload`, {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      return response.json();
    })
    .then((result: any) => {
      // Remove temporary message and add success message
      this.messages = this.messages.filter(msg => !msg.isTemporary);

      const successMessage: ChatMessage = {
        role: 'assistant',
        content: `✅ Document "${file.name}" uploaded and indexed successfully! ${result.chunks_indexed} chunks processed.${result.detected_offence_number ? ` Detected offence number: ${result.detected_offence_number}` : ''}`,
        timestamp: new Date()
      };
      this.messages.push(successMessage);

      // Auto-fill offence number if detected and not already set
      if (result.detected_offence_number && !this.currentOffenceNumber) {
        this.currentOffenceNumber = result.detected_offence_number;
      }

      this.isUploading = false;
    })
    .catch(error => {
      // Remove temporary message and add error message
      this.messages = this.messages.filter(msg => !msg.isTemporary);

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `❌ Document upload failed: ${error.message}`,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);

      this.isUploading = false;
      console.error('Upload error:', error);
    });

    // Clear file input
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
}
