import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../services/chat-store.service';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="message-group" [class.message-group--user]="message.role === 'user'">
      <div class="message-avatar">
        <span class="avatar-text">{{ message.role === 'user' ? getUserInitial() : 'L' }}</span>
      </div>
      
      <div class="message-content-wrapper">
        <div class="message-author">
          {{ message.role === 'user' ? 'You' : 'LEGID' }}
        </div>
        <div class="message-content" [innerHTML]="formatContent(message.content)"></div>
      </div>
    </div>
  `,
  styles: [`
    /* Message Group - ChatGPT Style */
    .message-group {
      display: flex;
      gap: 16px;
      padding: 24px 0;
      align-items: flex-start;
      max-width: 100%;
    }

    .message-group--user {
      flex-direction: row;
    }

    /* Avatar - ChatGPT Style */
    .message-avatar {
      width: 32px;
      height: 32px;
      flex-shrink: 0;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
    }

    .message-group--user .message-avatar {
      background: #5436DA;
      color: #ffffff;
    }

    .message-group:not(.message-group--user) .message-avatar {
      background: #10a37f;
      color: #ffffff;
    }

    .avatar-text {
      line-height: 1;
    }

    /* Content Wrapper */
    .message-content-wrapper {
      flex: 1;
      min-width: 0;
      max-width: 100%;
    }

    /* Author Name */
    .message-author {
      font-size: 14px;
      font-weight: 600;
      color: #eaeaea;
      margin-bottom: 8px;
    }

    /* Message Content - ChatGPT Style */
    .message-content {
      font-size: 16px;
      line-height: 1.75;
      color: #eaeaea;
      word-wrap: break-word;
      overflow-wrap: break-word;
    }

    .message-content p {
      margin: 16px 0;
    }

    .message-content p:first-child {
      margin-top: 0;
    }

    .message-content p:last-child {
      margin-bottom: 0;
    }

    /* Headings */
    .message-content h1,
    .message-content h2,
    .message-content h3 {
      margin: 24px 0 12px;
      line-height: 1.3;
      font-weight: 700;
      color: #eaeaea;
    }

    .message-content h1 {
      font-size: 24px;
    }

    .message-content h2 {
      font-size: 20px;
    }

    .message-content h3 {
      font-size: 18px;
    }

    /* Lists */
    .message-content ul,
    .message-content ol {
      margin: 16px 0;
      padding-left: 24px;
    }

    .message-content li {
      margin: 8px 0;
      line-height: 1.75;
      color: #eaeaea;
    }

    /* Links */
    .message-content a {
      color: #10a37f;
      text-decoration: underline;
      transition: opacity 150ms ease;
    }

    .message-content a:hover {
      opacity: 0.8;
    }

    /* Code Inline */
    .message-content code {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: "Söhne Mono", Monaco, "Andale Mono", monospace;
      font-size: 14px;
      color: #eaeaea;
    }

    /* Code Blocks */
    .message-content pre {
      background: #1a1a1e;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
      overflow-x: auto;
    }

    .message-content pre code {
      background: transparent;
      border: none;
      padding: 0;
      font-size: 14px;
      line-height: 1.6;
    }

    /* Strong/Bold */
    .message-content strong {
      font-weight: 700;
      color: #eaeaea;
    }

    /* Blockquote */
    .message-content blockquote {
      border-left: 3px solid rgba(255, 255, 255, 0.2);
      padding-left: 16px;
      margin: 16px 0;
      color: #a1a1aa;
      font-style: italic;
    }
  `]
})
export class MessageBubbleComponent {
  @Input() message!: Message;

  formatContent(content: string): string {
    // Convert markdown-style formatting to HTML
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^#{3}\s(.+)$/gm, '<h3>$1</h3>')
      .replace(/^#{2}\s(.+)$/gm, '<h2>$1</h2>')
      .replace(/^#{1}\s(.+)$/gm, '<h1>$1</h1>')
      .replace(/^•\s(.+)$/gm, '<li>$1</li>')
      .replace(/^-\s(.+)$/gm, '<li>$1</li>')
      .replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');

    // Wrap consecutive <li> in <ul>
    formatted = formatted.replace(/(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/gs, '<ul>$1</ul>');

    // Wrap in paragraph if not already wrapped
    if (!formatted.startsWith('<') && formatted.length > 0) {
      formatted = `<p>${formatted}</p>`;
    }

    return formatted;
  }

  formatTime(timestamp: Date): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  }

  getUserInitial(): string {
    // TODO: Get from auth service
    return 'U';
  }
}
