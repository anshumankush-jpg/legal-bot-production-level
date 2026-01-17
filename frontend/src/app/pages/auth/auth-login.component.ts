import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="auth-container">
      <!-- Left Panel: Branding -->
      <div class="auth-left">
        <div class="branding">
          <div class="logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            <h1>LegalAI</h1>
          </div>
          
          <h2 class="tagline">Your AI-Powered Legal Assistant</h2>
          
          <p class="description">
            Get instant answers to legal questions, generate professional documents, 
            and access comprehensive legal resources across Canada and the United States.
          </p>
          
          <div class="trust-indicators">
            <div class="trust-item">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="currentColor" stroke-width="2"/>
                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>Bank-level encryption</span>
            </div>
            <div class="trust-item">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 12C2 12 5 5 12 5C19 5 22 12 22 12C22 12 19 19 12 19C5 19 2 12 2 12Z" stroke="currentColor" stroke-width="2"/>
              </svg>
              <span>Your data stays private</span>
            </div>
            <div class="trust-item">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
              </svg>
              <span>Secure authentication</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Auth Form -->
      <div class="auth-right">
        <div class="auth-form-container">
          <!-- Role Tabs -->
          <div class="role-tabs">
            <button
              class="role-tab"
              [class.active]="selectedRole === 'customer'"
              (click)="selectedRole = 'customer'"
            >
              Join as Customer
            </button>
            <button
              class="role-tab"
              [class.active]="selectedRole === 'lawyer'"
              (click)="selectedRole = 'lawyer'"
            >
              Join as Lawyer
            </button>
          </div>

          <!-- Role Description -->
          <p class="role-description" *ngIf="selectedRole === 'customer'">
            Access legal information, chat with AI, and get help with basic legal questions.
          </p>
          <p class="role-description" *ngIf="selectedRole === 'lawyer'">
            Verified lawyers get access to document generation, amendments, and lead management. 
            Verification required.
          </p>

          <!-- OAuth Buttons -->
          <div class="oauth-buttons">
            <button
              class="oauth-btn google"
              (click)="signInWithGoogle()"
              [disabled]="loading"
            >
              <svg viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continue with Google</span>
            </button>

            <button
              class="oauth-btn microsoft"
              (click)="signInWithMicrosoft()"
              [disabled]="loading"
            >
              <svg viewBox="0 0 24 24">
                <path fill="#f25022" d="M0 0h11.377v11.372H0z"/>
                <path fill="#00a4ef" d="M12.623 0H24v11.372H12.623z"/>
                <path fill="#7fba00" d="M0 12.623h11.377V24H0z"/>
                <path fill="#ffb900" d="M12.623 12.623H24V24H12.623z"/>
              </svg>
              <span>Continue with Microsoft</span>
            </button>
          </div>

          <!-- Divider -->
          <div class="divider">
            <span>or</span>
          </div>

          <!-- Email/Password Form -->
          <form (ngSubmit)="handleEmailAuth()" *ngIf="!loading">
            <div class="form-group">
              <label for="email">Email address</label>
              <input
                id="email"
                type="email"
                [(ngModel)]="email"
                name="email"
                placeholder="you@example.com"
                required
                autocomplete="email"
              />
            </div>

            <div class="form-group">
              <label for="password">Password</label>
              <input
                id="password"
                type="password"
                [(ngModel)]="password"
                name="password"
                placeholder="Enter your password"
                required
                autocomplete="current-password"
                minlength="6"
              />
            </div>

            <button type="submit" class="submit-btn" [disabled]="loading">
              {{ isSignUp ? 'Create Account' : 'Sign In' }}
            </button>
          </form>

          <!-- Loading State -->
          <div class="loading-state" *ngIf="loading">
            <div class="spinner"></div>
            <p>{{ loadingMessage }}</p>
          </div>

          <!-- Error Message -->
          <div class="error-message" *ngIf="errorMessage">
            {{ errorMessage }}
          </div>

          <!-- Toggle Sign In/Sign Up -->
          <div class="auth-toggle">
            <span *ngIf="!isSignUp">
              Don't have an account?
              <button class="link-btn" (click)="isSignUp = true">Create account</button>
            </span>
            <span *ngIf="isSignUp">
              Already have an account?
              <button class="link-btn" (click)="isSignUp = false">Sign in</button>
            </span>
          </div>

          <!-- Forgot Password -->
          <div class="forgot-password" *ngIf="!isSignUp">
            <a routerLink="/auth/forgot-password" class="link-btn">Forgot password?</a>
          </div>

          <!-- Legal Notice -->
          <p class="legal-notice">
            By continuing, you agree to LegalAI's
            <a routerLink="/terms" target="_blank">Terms of Service</a> and
            <a routerLink="/privacy" target="_blank">Privacy Policy</a>.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    // ChatGPT-Style Auth Page
    $dark-bg: #212121;
    $dark-surface: #2a2a2a;
    $dark-border: #404040;
    $accent-teal: #00c9a7;
    $accent-blue: #3b82f6;
    $text-primary: #ececec;
    $text-secondary: #b4b4b4;

    .auth-container {
      display: flex;
      min-height: 100vh;
      background: $dark-bg;
      color: $text-primary;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    // Left Panel
    .auth-left {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4rem;
      background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
      border-right: 1px solid $dark-border;

      .branding {
        max-width: 500px;

        .logo {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 2rem;

          svg {
            width: 48px;
            height: 48px;
            color: $accent-teal;
          }

          h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, $accent-teal 0%, $accent-blue 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
          }
        }

        .tagline {
          font-size: 1.75rem;
          font-weight: 600;
          margin-bottom: 1.5rem;
          color: $text-primary;
        }

        .description {
          font-size: 1.125rem;
          line-height: 1.7;
          color: $text-secondary;
          margin-bottom: 3rem;
        }

        .trust-indicators {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;

          .trust-item {
            display: flex;
            align-items: center;
            gap: 1rem;

            svg {
              width: 24px;
              height: 24px;
              color: $accent-teal;
              flex-shrink: 0;
            }

            span {
              font-size: 1rem;
              color: $text-secondary;
            }
          }
        }
      }
    }

    // Right Panel
    .auth-right {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4rem;
      background: $dark-bg;
    }

    .auth-form-container {
      width: 100%;
      max-width: 420px;
    }

    // Role Tabs
    .role-tabs {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      padding: 0.25rem;
      background: $dark-surface;
      border-radius: 12px;

      .role-tab {
        padding: 0.875rem 1.5rem;
        background: transparent;
        border: none;
        border-radius: 10px;
        color: $text-secondary;
        font-weight: 600;
        font-size: 0.9375rem;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: rgba(255, 255, 255, 0.05);
          color: $text-primary;
        }

        &.active {
          background: linear-gradient(135deg, $accent-teal 0%, #00b894 100%);
          color: white;
          box-shadow: 0 4px 14px 0 rgba(0, 201, 167, 0.3);
        }
      }
    }

    .role-description {
      font-size: 0.875rem;
      color: $text-secondary;
      text-align: center;
      margin-bottom: 2rem;
      line-height: 1.5;
    }

    // OAuth Buttons
    .oauth-buttons {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-bottom: 1.5rem;

      .oauth-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        padding: 0.875rem 1.5rem;
        background: $dark-surface;
        border: 1px solid $dark-border;
        border-radius: 10px;
        color: $text-primary;
        font-weight: 600;
        font-size: 0.9375rem;
        cursor: pointer;
        transition: all 0.2s;

        svg {
          width: 20px;
          height: 20px;
        }

        &:hover:not(:disabled) {
          background: #3a3a3a;
          border-color: $accent-teal;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }

    // Divider
    .divider {
      text-align: center;
      margin: 2rem 0;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 1px;
        background: $dark-border;
      }

      span {
        position: relative;
        background: $dark-bg;
        padding: 0 1rem;
        color: $text-secondary;
        font-size: 0.875rem;
      }
    }

    // Email/Password Form
    .form-group {
      margin-bottom: 1.25rem;

      label {
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: $text-primary;
      }

      input {
        width: 100%;
        padding: 0.875rem 1rem;
        background: $dark-surface;
        border: 1px solid $dark-border;
        border-radius: 8px;
        color: $text-primary;
        font-size: 1rem;
        transition: all 0.2s;

        &::placeholder {
          color: #666;
        }

        &:focus {
          outline: none;
          border-color: $accent-teal;
          box-shadow: 0 0 0 3px rgba(0, 201, 167, 0.1);
        }
      }
    }

    .submit-btn {
      width: 100%;
      padding: 0.875rem;
      background: linear-gradient(135deg, $accent-teal 0%, #00b894 100%);
      border: none;
      border-radius: 10px;
      color: white;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 4px 14px 0 rgba(0, 201, 167, 0.3);

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(0, 201, 167, 0.4);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    // Loading State
    .loading-state {
      text-align: center;
      padding: 2rem;

      .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid $dark-border;
        border-top-color: $accent-teal;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 0 auto 1rem;
      }

      p {
        color: $text-secondary;
        font-size: 0.875rem;
      }
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    // Error Message
    .error-message {
      padding: 0.875rem;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid #ef4444;
      border-radius: 8px;
      color: #ef4444;
      font-size: 0.875rem;
      margin-top: 1rem;
      text-align: center;
    }

    // Auth Toggle
    .auth-toggle {
      text-align: center;
      margin-top: 1.5rem;
      font-size: 0.875rem;
      color: $text-secondary;

      .link-btn {
        background: none;
        border: none;
        color: $accent-teal;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }

    .forgot-password {
      text-align: center;
      margin-top: 1rem;

      .link-btn {
        background: none;
        border: none;
        color: $accent-teal;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    // Legal Notice
    .legal-notice {
      margin-top: 2rem;
      text-align: center;
      font-size: 0.75rem;
      color: #666;
      line-height: 1.5;

      a {
        color: $accent-teal;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    // Responsive
    @media (max-width: 1024px) {
      .auth-container {
        flex-direction: column;
      }

      .auth-left {
        padding: 2rem;
        border-right: none;
        border-bottom: 1px solid $dark-border;
      }

      .auth-right {
        padding: 2rem;
      }
    }
  `]
})
export class AuthLoginComponent implements OnInit {
  selectedRole: 'customer' | 'lawyer' = 'customer';
  isSignUp: boolean = false;
  loading: boolean = false;
  loadingMessage: string = '';
  errorMessage: string = '';
  
  email: string = '';
  password: string = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    // Check if already authenticated
    if (this.authService.isAuthenticated()) {
      // Redirect based on role
      const user = this.authService.getCurrentUserSync();
      if (user?.role === 'lawyer' && user.lawyer_status === 'approved') {
        this.router.navigate(['/lawyer/dashboard']);
      } else if (user?.role === 'customer') {
        this.router.navigate(['/app']);
      }
    }
  }

  async signInWithGoogle(): Promise<void> {
    this.loading = true;
    this.loadingMessage = 'Signing in with Google...';
    this.errorMessage = '';

    try {
      await this.authService.signInWithGoogle(this.selectedRole);
      // Navigation handled by auth service
    } catch (error: any) {
      this.errorMessage = error.message || 'Google sign-in failed. Please try again.';
    } finally {
      this.loading = false;
      this.loadingMessage = '';
    }
  }

  async signInWithMicrosoft(): Promise<void> {
    this.loading = true;
    this.loadingMessage = 'Signing in with Microsoft...';
    this.errorMessage = '';

    try {
      await this.authService.signInWithMicrosoft(this.selectedRole);
      // Navigation handled by auth service
    } catch (error: any) {
      this.errorMessage = error.message || 'Microsoft sign-in failed. Please try again.';
    } finally {
      this.loading = false;
      this.loadingMessage = '';
    }
  }

  async handleEmailAuth(): Promise<void> {
    if (!this.email || !this.password) {
      this.errorMessage = 'Please enter email and password';
      return;
    }

    this.loading = true;
    this.loadingMessage = this.isSignUp ? 'Creating account...' : 'Signing in...';
    this.errorMessage = '';

    try {
      if (this.isSignUp) {
        await this.authService.createAccountWithEmail(this.email, this.password, this.selectedRole);
      } else {
        await this.authService.signInWithEmail(this.email, this.password, this.selectedRole);
      }
      // Navigation handled by auth service
    } catch (error: any) {
      this.errorMessage = error.message || (this.isSignUp ? 'Account creation failed' : 'Sign in failed');
    } finally {
      this.loading = false;
      this.loadingMessage = '';
    }
  }

  private router: any; // Inject Router if needed
}
  `]
})
export class AuthLoginComponent implements OnInit {
  // Component implementation in template above
}
