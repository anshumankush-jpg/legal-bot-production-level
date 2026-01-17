import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { ProfileMenuComponent } from './profile-menu.component';
import { AuthService, User } from '../../services/auth.service';
import { ChatStoreService } from '../../services/chat-store.service';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, FormsModule, ProfileMenuComponent],
  templateUrl: './topbar.component.html',
  styleUrls: ['./topbar.component.scss']
})
export class TopbarComponent implements OnInit, OnDestroy {
  currentLanguage = 'English';
  country = 'Canada';
  province = 'ON';
  region = 'ON';
  lawType = 'Wills, Estates, and Trusts';
  andyStatus = 'OFF';
  offenceNumber = '';
  currentUser: User | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private chatStore: ChatStoreService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Subscribe to current user
    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        this.currentUser = user;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  toggleAndyStatus(): void {
    this.andyStatus = this.andyStatus === 'OFF' ? 'ON' : 'OFF';
  }

  getUserInitials(): string {
    if (!this.currentUser) return 'U';
    const name = this.currentUser.display_name || this.currentUser.email;
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  createNewChat(): void {
    const newId = this.chatStore.createConversation();
    this.router.navigate(['/app/chat', newId]);
  }
}
