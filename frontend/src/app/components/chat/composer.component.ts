import { Component, Output, EventEmitter, Input, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-composer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="composer__bar">
      <button 
        class="attach-btn" 
        type="button"
        [disabled]="disabled"
        title="Attach file"
      >
        <span style="font-size: 18px;">📎</span>
      </button>

      <input
        #textInput
        [(ngModel)]="message"
        (keydown.enter)="onEnter($event)"
        [disabled]="disabled"
        placeholder="Ask about legal documents or traffic laws..."
        class="composer__input"
        type="text"
      />

      <button 
        class="mic-btn" 
        type="button"
        [disabled]="disabled"
        title="Voice input"
      >
        <span style="font-size: 18px;">🎤</span>
      </button>

      <button 
        class="send-btn" 
        type="button"
        (click)="send()"
        [disabled]="!message.trim() || disabled"
        title="Send message"
      >
        <span style="font-size: 18px;">➤</span>
      </button>
    </div>

    <div class="composer__hint">
      This is general information only, not legal advice. Consult a licensed lawyer for specific cases.
    </div>
  `,
  styles: [`
    .composer__bar {
      display: grid;
      grid-template-columns: auto 1fr auto auto;
      gap: 10px;
      align-items: center;
      height: var(--composer-h);
      border-radius: 16px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      padding: 0 10px;
      box-shadow: var(--shadow-soft);
    }
    .composer__bar:focus-within {
      border-color: rgba(34,197,94,0.45);
      background: rgba(255,255,255,0.05);
    }

    .attach-btn, .mic-btn, .send-btn {
      width: 38px;
      height: 38px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      display: grid;
      place-items: center;
      cursor: pointer;
      transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }
    .attach-btn:hover, .mic-btn:hover, .send-btn:hover {
      background: rgba(255,255,255,0.06);
      border-color: var(--border-2);
    }
    .attach-btn:active, .mic-btn:active, .send-btn:active { transform: translateY(1px); }

    .send-btn {
      border-color: rgba(34,197,94,0.30);
      background: rgba(34,197,94,0.16);
    }
    .send-btn:hover {
      background: rgba(34,197,94,0.20);
      border-color: rgba(34,197,94,0.45);
    }

    .composer__input {
      width: 100%;
      height: calc(var(--composer-h) - 14px);
      padding: 0 6px;
      border: 0;
      outline: none;
      background: transparent;
      color: var(--text);
      font-size: 14px;
    }
    .composer__hint {
      text-align: center;
      font-size: 12px;
      color: var(--text-3);
    }
  `]
})
export class ComposerComponent {
  @Input() disabled = false;
  @Output() sendMessage = new EventEmitter<string>();
  @ViewChild('textInput') textInput?: ElementRef;

  message = '';

  onEnter(event: KeyboardEvent): void {
    if (event.shiftKey) {
      return; // Allow shift+enter for new lines
    }
    event.preventDefault();
    this.send();
  }

  onInput(): void {
    this.adjustTextareaHeight();
  }

  send(): void {
    if (!this.message.trim() || this.disabled) return;

    this.sendMessage.emit(this.message.trim());
    this.message = '';
    this.adjustTextareaHeight();
  }

  private adjustTextareaHeight(): void {
    if (this.textInput) {
      const textarea = this.textInput.nativeElement;
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  }
}
