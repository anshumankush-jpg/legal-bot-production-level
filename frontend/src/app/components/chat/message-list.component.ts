import { Component, Input, Output, EventEmitter, AfterViewChecked, ViewChild, ElementRef, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../services/chat-store.service';
import { MessageBubbleComponent } from './message-bubble.component';
import { TypingIndicatorComponent } from './typing-indicator.component';

@Component({
  selector: 'app-message-list',
  standalone: true,
  imports: [CommonModule, MessageBubbleComponent, TypingIndicatorComponent],
  template: `
    <!-- Welcome state when no messages -->
    <div *ngIf="messages.length === 0 && !isTyping" class="welcome-container">
      <div class="welcome-content">
        <!-- Header Section -->
        <div class="welcome-header">
          <div class="welcome-logo">
            <div class="logo-icon-large">⚖️</div>
            <h1 class="welcome-title">Welcome to LEGID</h1>
          </div>
          <p class="welcome-subtitle">Your Legal Intelligence Assistant!</p>
          <p class="welcome-description">
            Thank you for reaching out. I'm here to assist you with your <strong>Constitutional Law</strong> matter.
          </p>
        </div>

        <!-- Instructions Card -->
        <div class="instructions-card">
          <h3 class="instructions-title">How may I assist you today?</h3>
          <p class="instructions-subtitle">Please provide a detailed description of your legal situation, including:</p>
          
          <ol class="instructions-list">
            <li><strong>The nature</strong> of your legal issue or question</li>
            <li><strong>Relevant dates,</strong> locations, and parties involved</li>
            <li><strong>Any documents</strong> or evidence you have</li>
            <li><strong>What outcome</strong> or information you're seeking</li>
          </ol>

          <div class="disclaimer">
            <svg class="disclaimer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <p>I'll provide you with relevant legal information based on official sources and statutes. 
            Please note that this is <strong>general legal information, not legal advice.</strong></p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h4 class="quick-actions-title">Or try one of these:</h4>
          <div class="action-cards">
            <button class="action-card" (click)="onPromptClick('What are my rights if I receive a traffic ticket in Ontario?')">
              <div class="action-icon">🚗</div>
              <div class="action-content">
                <div class="action-title">Traffic Tickets</div>
                <div class="action-description">Learn about your rights and options</div>
              </div>
            </button>
            
            <button class="action-card" (click)="onPromptClick('How do I create a will in Ontario?')">
              <div class="action-icon">📜</div>
              <div class="action-content">
                <div class="action-title">Wills & Estates</div>
                <div class="action-description">Estate planning guidance</div>
              </div>
          </button>
            
            <button class="action-card" (click)="onPromptClick('What are the steps to start a small business in Canada?')">
              <div class="action-icon">💼</div>
              <div class="action-content">
                <div class="action-title">Business Law</div>
                <div class="action-description">Start your business legally</div>
              </div>
          </button>

            <button class="action-card" (click)="onPromptClick('What are my tenant rights in Ontario?')">
              <div class="action-icon">🏠</div>
              <div class="action-content">
                <div class="action-title">Tenant Rights</div>
                <div class="action-description">Housing and rental law</div>
              </div>
          </button>
          </div>
        </div>
      </div>
    </div>

    <app-message-bubble
      *ngFor="let message of messages; trackBy: trackMessage"
      [message]="message"
    ></app-message-bubble>

    <app-typing-indicator *ngIf="isTyping"></app-typing-indicator>
  `,
  styles: [`
    /* Welcome Container */
    .welcome-container {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100%;
      padding: 3rem 2rem;
      animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .welcome-content {
      max-width: 900px;
      width: 100%;
    }

    /* Header Section */
    .welcome-header {
      text-align: center;
      margin-bottom: 2.5rem;
    }

    .welcome-logo {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .logo-icon-large {
      font-size: 4rem;
      line-height: 1;
      filter: drop-shadow(0 0 20px rgba(16, 163, 127, 0.4));
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
    }

    .welcome-title {
      font-size: 2.5rem;
      font-weight: 800;
      color: #FFFFFF;
      margin: 0;
      letter-spacing: 0.02em;
    }

    .welcome-subtitle {
      font-size: 1.25rem;
      color: #F5F5F5;
      font-weight: 600;
      margin: 0.5rem 0 1rem;
    }

    .welcome-description {
      font-size: 1rem;
      color: #B0B0B0;
      line-height: 1.6;
      margin: 0;
    }

    .welcome-description strong {
      color: #00BCD4;
      font-weight: 600;
    }

    /* Instructions Card - ChatGPT Style */
    .instructions-card {
      background: #1a1a1e;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2.5rem;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    .instructions-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #eaeaea;
      margin: 0 0 0.75rem;
    }

    .instructions-subtitle {
      font-size: 1rem;
      color: #a1a1aa;
      margin: 0 0 1.5rem;
    }

    .instructions-list {
      list-style: none;
      counter-reset: item;
      padding: 0;
      margin: 0 0 2rem;
    }

    .instructions-list li {
      counter-increment: item;
      position: relative;
      padding-left: 2.5rem;
      margin-bottom: 1rem;
      font-size: 0.95rem;
      color: #F5F5F5;
      line-height: 1.6;
    }

    .instructions-list li::before {
      content: counter(item);
      position: absolute;
      left: 0;
      top: 0;
      width: 28px;
      height: 28px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.875rem;
      color: #eaeaea;
    }

    .instructions-list li strong {
      color: #eaeaea;
      font-weight: 600;
    }

    /* Disclaimer - ChatGPT Style */
    .disclaimer {
      display: flex;
      gap: 1rem;
      padding: 1.25rem;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
    }

    .disclaimer-icon {
      width: 24px;
      height: 24px;
      color: #eaeaea;
      flex-shrink: 0;
    }

    .disclaimer p {
      margin: 0;
      font-size: 0.875rem;
      color: #a1a1aa;
      line-height: 1.6;
    }

    .disclaimer strong {
      color: #eaeaea;
      font-weight: 600;
    }

    /* Quick Actions */
    .quick-actions {
      margin-top: 2.5rem;
    }

    .quick-actions-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #F5F5F5;
      margin: 0 0 1.25rem;
      text-align: center;
    }

    .action-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }

    /* Action Cards - ChatGPT Style */
    .action-card {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1.25rem;
      background: #1a1a1e;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      cursor: pointer;
      transition: background 150ms ease, border-color 150ms ease, transform 150ms ease;
      text-align: left;
    }

    .action-card:hover {
      background: #232329;
      border-color: rgba(255, 255, 255, 0.16);
      transform: translateY(-1px);
    }

    .action-card:active {
      transform: translateY(0);
    }

    .action-icon {
      font-size: 2rem;
      line-height: 1;
      flex-shrink: 0;
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .action-content {
      flex: 1;
      min-width: 0;
    }

    .action-title {
      font-size: 1rem;
      font-weight: 600;
      color: #eaeaea;
      margin-bottom: 0.25rem;
    }

    .action-description {
      font-size: 0.875rem;
      color: #a1a1aa;
      line-height: 1.4;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .welcome-container {
        padding: 2rem 1rem;
      }

      .welcome-title {
        font-size: 2rem;
      }

      .logo-icon-large {
        font-size: 3rem;
      }

      .instructions-card {
        padding: 1.5rem;
      }

      .action-cards {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class MessageListComponent implements AfterViewChecked, OnChanges {
  @Input() messages: Message[] = [];
  @Input() isTyping = false;
  @Output() promptClick = new EventEmitter<string>();
  @ViewChild('messageList') messageList?: ElementRef;

  private shouldScroll = false;

  onPromptClick(text: string): void {
    this.promptClick.emit(text);
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['messages'] || changes['isTyping']) {
      this.shouldScroll = true;
    }
  }

  trackMessage(index: number, message: Message): string {
    return message.id;
  }

  private scrollToBottom(): void {
    if (this.messageList) {
      const element = this.messageList.nativeElement;
      // Check if user has scrolled up manually
      const isNearBottom = element.scrollHeight - element.scrollTop - element.clientHeight < 100;
      
      // Only auto-scroll if user is near the bottom (not scrolled up)
      if (isNearBottom || this.messages.length === 0) {
        setTimeout(() => {
          element.scrollTop = element.scrollHeight;
        }, 0);
      }
    }
  }
}
