import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { UserContextService } from '../../services/user-context.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-container">
      <div class="profile-card">
        <h1>Profile Settings</h1>
        
        <div class="section" *ngIf="preferences">
          <h2>User Preferences</h2>
          <div class="preference-item">
            <span class="label">Language:</span>
            <span class="value">{{ preferences.language }}</span>
          </div>
          <div class="preference-item">
            <span class="label">Country:</span>
            <span class="value">{{ preferences.country }}</span>
          </div>
          <div class="preference-item">
            <span class="label">Province/State:</span>
            <span class="value">{{ preferences.provinceOrState }}</span>
          </div>
          <div class="preference-item" *ngIf="preferences.offenceNumber">
            <span class="label">Offence Number:</span>
            <span class="value">{{ preferences.offenceNumber }}</span>
          </div>
        </div>

        <div class="section">
          <h2>Actions</h2>
          <button class="btn-secondary" (click)="editPreferences()">Edit Preferences</button>
          <button class="btn-danger" (click)="logout()">Logout</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .profile-container {
      min-height: 100vh;
      padding: 2rem;
      background: #f5f5f5;
    }
    
    .profile-card {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .section {
      margin-bottom: 2rem;
      
      h2 {
        color: #0B1F3B;
        margin-bottom: 1rem;
      }
    }
    
    .preference-item {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem 0;
      border-bottom: 1px solid #e0e0e0;
      
      .label {
        font-weight: 500;
        color: #757575;
      }
      
      .value {
        color: #0B1F3B;
        font-weight: 600;
      }
    }
    
    .btn-secondary, .btn-danger {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      border: none;
      font-weight: 600;
      cursor: pointer;
      margin-right: 1rem;
      margin-top: 1rem;
    }
    
    .btn-secondary {
      background: #00BCD4;
      color: white;
    }
    
    .btn-danger {
      background: #F44336;
      color: white;
    }
  `]
})
export class ProfileComponent implements OnInit {
  preferences: any = null;

  constructor(
    private userContext: UserContextService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.preferences = this.userContext.getPreferences();
  }

  editPreferences(): void {
    this.router.navigate(['/setup']);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}