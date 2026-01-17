import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-typing-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="message">
      <div class="message__avatar">AI</div>
      <div>
        <div class="message__meta">
          <span>LEGID</span>
        </div>
        <div class="message__bubble">
          <div class="typing">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .message {
      display: grid;
      grid-template-columns: 38px 1fr;
      gap: 12px;
      align-items: start;
    }
    .message__avatar {
      width: 34px; height: 34px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      display: grid;
      place-items: center;
      color: var(--text-2);
      font-weight: 700;
      font-size: 0.75rem;
    }
    .message__bubble {
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      background: rgba(255,255,255,0.03);
      padding: 14px;
      box-shadow: var(--shadow-soft);
    }
    .message__meta {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 10px;
      color: var(--text-3);
      font-size: 12px;
    }
    .typing {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
    }
    .dot {
      width: 6px; height: 6px;
      border-radius: 999px;
      background: rgba(255,255,255,0.55);
      animation: blink 1.2s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.15s; }
    .dot:nth-child(3) { animation-delay: 0.30s; }
    @keyframes blink {
      0%, 80%, 100% { opacity: 0.25; transform: translateY(0); }
      40% { opacity: 0.95; transform: translateY(-2px); }
    }
  `]
})
export class TypingIndicatorComponent {}
