import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile-menu',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-menu">
      <button class="profile-trigger" (click)="toggleMenu()">
        <div class="avatar">AK</div>
        <span class="username">Achint Pal singh</span>
        <span class="dropdown-icon">▼</span>
      </button>

      <div class="profile-dropdown" *ngIf="isOpen" (click)="$event.stopPropagation()">
        <button class="menu-item" (click)="navigate('/app/personalization')">
          <span class="menu-icon">👤</span>
          <span>Personalization</span>
        </button>
        <button class="menu-item" (click)="navigate('/app/settings')">
          <span class="menu-icon">⚙️</span>
          <span>Settings</span>
        </button>
        <button class="menu-item" (click)="handleHelp()">
          <span class="menu-icon">❓</span>
          <span>Help</span>
        </button>
        <div class="menu-divider"></div>
        <button class="menu-item logout" (click)="handleLogout()">
          <span class="menu-icon">🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .profile-menu {
      position: relative;
    }

    .profile-trigger {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem 0.875rem;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius-pill);
      color: var(--text);
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: var(--card2);
        border-color: var(--accent);
      }
    }

    .avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .username {
      color: var(--text-muted);
    }

    .dropdown-icon {
      font-size: 0.625rem;
      opacity: 0.6;
    }

    .profile-dropdown {
      position: absolute;
      top: calc(100% + 0.5rem);
      right: 0;
      min-width: 200px;
      background: var(--card2);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow);
      padding: 0.5rem;
      z-index: 1000;
      animation: slideDown 0.2s ease;
    }

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-8px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .menu-item {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: transparent;
      border: none;
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      font-size: 0.875rem;
      text-align: left;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: var(--card);
        color: var(--text);
      }

      &.logout {
        color: #ef4444;

        &:hover {
          background: rgba(239, 68, 68, 0.1);
        }
      }
    }

    .menu-icon {
      font-size: 1.125rem;
    }

    .menu-divider {
      height: 1px;
      background: var(--border);
      margin: 0.5rem 0;
    }
  `]
})
export class ProfileMenuComponent {
  isOpen = false;

  constructor(private router: Router) {
    // Close menu when clicking outside
    document.addEventListener('click', () => {
      this.isOpen = false;
    });
  }

  toggleMenu(): void {
    this.isOpen = !this.isOpen;
  }

  navigate(path: string): void {
    this.router.navigate([path]);
    this.isOpen = false;
  }

  handleHelp(): void {
    console.log('Opening help...');
    this.isOpen = false;
  }

  handleLogout(): void {
    console.log('Logging out...');
    localStorage.clear();
    this.router.navigate(['/']);
    this.isOpen = false;
  }
}
