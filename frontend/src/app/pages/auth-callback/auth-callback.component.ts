import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-auth-callback',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="callback-container">
      <div class="spinner"></div>
      <h2>{{ message }}</h2>
      <p *ngIf="error" class="error">{{ error }}</p>
    </div>
  `,
  styles: [`
    .callback-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #fff;
      text-align: center;
      padding: 2rem;
    }

    .spinner {
      border: 4px solid #374151;
      border-top: 4px solid #3b82f6;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      animation: spin 1s linear infinite;
      margin-bottom: 1.5rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    h2 {
      font-size: 1.5rem;
      margin: 0;
      color: #e5e7eb;
    }

    p {
      margin-top: 1rem;
      color: #9ca3af;
    }

    .error {
      color: #ef4444;
    }
  `]
})
export class AuthCallbackComponent implements OnInit {
  message = 'Completing authentication...';
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const authSuccess = params['auth'];
      const errorParam = params['error'];

      if (errorParam) {
        this.error = 'Authentication failed. Please try again.';
        this.message = 'Error';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      } else if (authSuccess === 'success') {
        this.message = 'Authentication successful!';
        setTimeout(() => {
          this.router.navigate(['/chat']);
        }, 1000);
      } else {
        // Still processing
        setTimeout(() => {
          this.router.navigate(['/chat']);
        }, 2000);
      }
    });
  }
}
