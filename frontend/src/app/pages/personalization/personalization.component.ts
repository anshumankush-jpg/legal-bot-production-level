import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { PreferencesService, Preferences } from '../../services/preferences.service';
import { Subscription } from 'rxjs';

interface UserProfile {
  user_id: string;
  display_name?: string;
  username?: string;
  avatar_url?: string;
  phone?: string;
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  province_state?: string;
  postal_zip?: string;
  country?: string;
  preferences_json?: {
    theme?: 'dark' | 'light';
    font_size?: 'small' | 'medium' | 'large';
    response_style?: 'concise' | 'balanced' | 'detailed';
    legal_tone?: 'neutral' | 'firm' | 'very_formal';
    auto_read_responses?: boolean;
  };
  updated_at: string;
}

@Component({
  selector: 'app-personalization',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule],
  template: `
    <div class="personalization-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <button class="back-btn" (click)="goBack()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5"></path>
              <path d="M12 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1>Personalization</h1>
        </div>
        <p class="page-description">
          Customize your experience to match your preferences.
        </p>
      </div>

      <!-- Content -->
      <div class="page-content">
        <!-- Theme Section -->
        <div class="settings-section">
          <h2>Appearance</h2>

          <div class="setting-group">
            <h3>Theme</h3>
            <p class="setting-description">Choose your preferred color scheme.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.theme === 'dark'">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  [(ngModel)]="preferences.theme"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Dark</div>
                  <div class="radio-description">Easy on the eyes in low light</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.theme === 'light'">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  [(ngModel)]="preferences.theme"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Light</div>
                  <div class="radio-description">Classic bright interface</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.theme === 'system'">
                <input
                  type="radio"
                  name="theme"
                  value="system"
                  [(ngModel)]="preferences.theme"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">System</div>
                  <div class="radio-description">Match your device settings</div>
                </div>
              </label>
            </div>
          </div>

          <div class="setting-group">
            <h3>Font Size</h3>
            <p class="setting-description">Adjust the text size for better readability.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.fontSize === 'small'">
                <input
                  type="radio"
                  name="fontSize"
                  value="small"
                  [(ngModel)]="preferences.fontSize"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Small</div>
                  <div class="radio-description">Compact and space-efficient</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.fontSize === 'medium'">
                <input
                  type="radio"
                  name="fontSize"
                  value="medium"
                  [(ngModel)]="preferences.fontSize"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Medium</div>
                  <div class="radio-description">Balanced and comfortable</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.fontSize === 'large'">
                <input
                  type="radio"
                  name="fontSize"
                  value="large"
                  [(ngModel)]="preferences.fontSize"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Large</div>
                  <div class="radio-description">Enhanced readability</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Response Style Section -->
        <div class="settings-section">
          <h2>Response Style</h2>

          <div class="setting-group">
            <h3>Detail Level</h3>
            <p class="setting-description">Choose how detailed you want AI responses to be.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.responseStyle === 'concise'">
                <input
                  type="radio"
                  name="responseStyle"
                  value="concise"
                  [(ngModel)]="preferences.responseStyle"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Concise</div>
                  <div class="radio-description">Brief, to-the-point answers</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.responseStyle === 'detailed'">
                <input
                  type="radio"
                  name="responseStyle"
                  value="detailed"
                  [(ngModel)]="preferences.responseStyle"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Detailed</div>
                  <div class="radio-description">Thorough explanations with examples</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.responseStyle === 'legal_format'">
                <input
                  type="radio"
                  name="responseStyle"
                  value="legal_format"
                  [(ngModel)]="preferences.responseStyle"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Legal Format</div>
                  <div class="radio-description">Formal legal document style</div>
                </div>
              </label>
            </div>
          </div>

          <div class="setting-group">
            <h3>Legal Tone</h3>
            <p class="setting-description">Set the communication style for legal responses.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.legal_tone === 'neutral'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="neutral"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Neutral</div>
                  <div class="radio-description">Professional and balanced</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.legal_tone === 'firm'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="firm"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Firm</div>
                  <div class="radio-description">Direct and assertive</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.legal_tone === 'very_formal'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="very_formal"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Very Formal</div>
                  <div class="radio-description">Traditional legal language</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Voice Settings Section -->
        <div class="settings-section">
          <h2>Voice & Audio</h2>
          <div class="setting-group">
            <div class="setting-item">
              <div class="setting-content">
                <div class="setting-label">
                  <div class="setting-title">Auto-Read Responses</div>
                  <div class="setting-description">
                    Automatically play audio for AI responses using text-to-speech
                  </div>
                </div>
                <label class="toggle-switch">
                  <input
                    type="checkbox"
                    [(ngModel)]="preferences.autoReadResponses"
                    (change)="onPreferenceChange()"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Language Section -->
        <div class="settings-section">
          <h2>Language</h2>
          <div class="setting-group">
            <h3>Interface Language</h3>
            <p class="setting-description">Choose your preferred language for the interface.</p>
            <select [(ngModel)]="preferences.language" (change)="onPreferenceChange()" class="language-select">
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
        </div>

        <!-- Preview Section -->
        <div class="settings-section">
          <h2>Preview</h2>
          <div class="preview-notice">
            <div class="preview-icon">💡</div>
            <div class="preview-content">
              <h3>Changes Applied</h3>
              <p>Your preferences will be saved automatically and applied to your experience.</p>
              <p class="preview-note">
                Note: Some visual changes may require refreshing the page to take full effect.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div *ngIf="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Loading preferences...</p>
      </div>

      <!-- Status Messages -->
      <div class="status-message" *ngIf="saveError">
        <div class="error-message">
          {{ saveError }}
        </div>
      </div>

      <div class="status-message" *ngIf="saveSuccess">
        <div class="success-message">
          Preferences saved successfully!
        </div>
      </div>
    </div>
  `,
  styles: [`
    .personalization-page {
      min-height: 100vh;
      background: #212121;
      color: #ececec;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    }

    .page-header {
      padding: 2rem;
      border-bottom: 1px solid #404040;
    }

    .header-content {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.5rem;
    }

    .back-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid #404040;
      border-radius: 8px;
      color: #9ca3af;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .back-btn:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: #00bcd4;
      color: #00bcd4;
    }

    .page-header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0;
      color: #ececec;
    }

    .page-description {
      color: #9ca3af;
      margin: 0;
      font-size: 0.875rem;
    }

    .page-content {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }

    .settings-section {
      margin-bottom: 3rem;
    }

    .settings-section h2 {
      font-size: 1.25rem;
      font-weight: 600;
      color: #ececec;
      margin: 0 0 1.5rem 0;
    }

    .setting-group {
      margin-bottom: 2rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border-radius: 12px;
      border: 1px solid #404040;
    }

    .setting-group h3 {
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
      margin: 0 0 0.5rem 0;
    }

    .setting-description {
      color: #9ca3af;
      font-size: 0.875rem;
      margin: 0 0 1.5rem 0;
      line-height: 1.5;
    }

    .radio-group {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .radio-option {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      padding: 1rem;
      border: 2px solid #404040;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s ease;
      background: #1f1f1f;
    }

    .radio-option:hover {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.05);
    }

    .radio-option.selected {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.1);
    }

    .radio-option input[type="radio"] {
      display: none;
    }

    .radio-content {
      flex: 1;
    }

    .radio-label {
      font-weight: 500;
      color: #ececec;
      margin-bottom: 0.25rem;
    }

    .radio-description {
      font-size: 0.875rem;
      color: #9ca3af;
      line-height: 1.4;
    }

    .preview-notice {
      display: flex;
      gap: 1rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border-radius: 12px;
      border: 1px solid #404040;
    }

    .preview-icon {
      font-size: 1.5rem;
      flex-shrink: 0;
    }

    .preview-content h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
    }

    .preview-content p {
      margin: 0 0 0.5rem 0;
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .preview-note {
      font-style: italic;
      color: #6b7280;
    }

    .status-message {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      max-width: 400px;
      z-index: 1000;
    }

    .error-message {
      background: #fef2f2;
      color: #991b1b;
      padding: 1rem;
      border-radius: 8px;
      border: 1px solid #fecaca;
      font-size: 0.875rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .success-message {
      background: #f0fdf4;
      color: #166534;
      padding: 1rem;
      border-radius: 8px;
      border: 1px solid #bbf7d0;
      font-size: 0.875rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
      .page-header {
        padding: 1rem;
      }

      .header-content {
        gap: 0.75rem;
      }

      .page-header h1 {
        font-size: 1.25rem;
      }

      .page-content {
        padding: 1rem;
      }

      .setting-group {
        padding: 1rem;
      }

      .radio-option {
        padding: 0.75rem;
      }

      .preview-notice {
        flex-direction: column;
        text-align: center;
      }

      .status-message {
        left: 1rem;
        right: 1rem;
        bottom: 1rem;
        max-width: none;
      }
    }

    .loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      color: #ececec;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #404040;
      border-top: 4px solid #00bcd4;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .language-select {
      width: 100%;
      padding: 0.75rem;
      background: #1f1f1f;
      border: 2px solid #404040;
      border-radius: 8px;
      color: #ececec;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .language-select:hover {
      border-color: #00bcd4;
    }

    .language-select:focus {
      outline: none;
      border-color: #00bcd4;
      box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1);
    }
  `]
})
export class PersonalizationComponent implements OnInit, OnDestroy {
  preferences: Preferences = {
    theme: 'dark',
    fontSize: 'medium',
    responseStyle: 'detailed',
    language: 'en',
    autoReadResponses: false
  };

  saveError = '';
  saveSuccess = false;
  isLoading = false;
  private saveTimeout: any;
  private subscriptions: Subscription[] = [];

  constructor(
    private router: Router,
    private preferencesService: PreferencesService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadPreferences();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
  }

  loadPreferences(): void {
    this.isLoading = true;
    const sub = this.preferencesService.getPreferences().subscribe({
      next: (prefs) => {
        this.preferences = { ...this.preferences, ...prefs };
        this.isLoading = false;
        console.log('✅ Preferences loaded:', prefs);
      },
      error: (error) => {
        console.error('❌ Failed to load preferences:', error);
        this.isLoading = false;
        
        // Try loading from localStorage as fallback
        const localPrefs = this.preferencesService.loadFromLocalStorage();
        if (localPrefs) {
          this.preferences = { ...this.preferences, ...localPrefs };
          this.snackBar.open('Loaded preferences from cache. Some features may be limited.', 'Dismiss', {
            duration: 5000
          });
        } else {
          this.snackBar.open('Failed to load preferences. Using defaults.', 'Dismiss', {
            duration: 5000
          });
        }
      }
    });
    this.subscriptions.push(sub);
  }

  onPreferenceChange(): void {
    // Auto-save after a short delay
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.saveTimeout = setTimeout(() => {
      this.savePreferences();
    }, 1000); // 1 second delay
  }

  savePreferences(): void {
    this.saveError = '';
    this.saveSuccess = false;

    const sub = this.preferencesService.savePreferences(this.preferences).subscribe({
      next: (response) => {
        this.saveSuccess = true;
        this.snackBar.open('Preferences saved successfully!', 'Dismiss', {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
        setTimeout(() => {
          this.saveSuccess = false;
        }, 3000);
        console.log('✅ Preferences saved:', response);
      },
      error: (error) => {
        const errorMsg = error.message || 'Failed to save preferences';
        this.saveError = errorMsg;
        this.snackBar.open(`Error: ${errorMsg}`, 'Dismiss', {
          duration: 5000,
          panelClass: ['error-snackbar']
        });
        console.error('❌ Failed to save preferences:', {
          error,
          message: errorMsg,
          preferences: this.preferences
        });
        setTimeout(() => {
          this.saveError = '';
        }, 5000);
      }
    });
    this.subscriptions.push(sub);
  }

  goBack(): void {
    this.router.navigate(['/']);
  }
}