import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { ChatService, Conversation } from '../../services/chat.service';
import { AuthService, User } from '../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit, OnDestroy {
  searchQuery = '';
  conversations: Conversation[] = [];
  activeConversationId: string | null = null;
  currentUser: User | null = null;
  showProfileMenu = false;

  private destroy$ = new Subject<void>();

  constructor(
    private chatService: ChatService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Subscribe to conversations
    this.chatService.conversations$
      .pipe(takeUntil(this.destroy$))
      .subscribe(conversations => {
        this.conversations = this.searchQuery 
          ? this.chatService.searchConversations(this.searchQuery)
          : conversations;
      });

    // Subscribe to active conversation
    this.chatService.activeConversation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(id => {
        this.activeConversationId = id;
      });

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

  onSearchChange(): void {
    this.conversations = this.chatService.searchConversations(this.searchQuery);
  }

  createNewChat(): void {
    this.chatService.createConversation().subscribe({
      next: (conv) => {
        this.router.navigate(['/app/chat', conv.conversation_id]);
      },
      error: (err) => {
        console.error('Failed to create conversation:', err);
      }
    });
  }

  selectConversation(conversation: Conversation): void {
    this.chatService.setActiveConversation(conversation.conversation_id);
    this.router.navigate(['/app/chat', conversation.conversation_id]);
  }

  deleteConversation(conversation: Conversation, event: Event): void {
    event.stopPropagation();
    if (confirm(`Delete "${conversation.title}"?`)) {
      this.chatService.deleteConversation(conversation.conversation_id).subscribe({
        error: (err) => {
          console.error('Failed to delete conversation:', err);
        }
      });
    }
  }

  toggleProfileMenu(): void {
    this.showProfileMenu = !this.showProfileMenu;
  }

  handleProfileAction(action: string): void {
    this.showProfileMenu = false;
    
    switch (action) {
      case 'personalization':
        this.router.navigate(['/app/personalization']);
        break;
      case 'settings':
        this.router.navigate(['/app/settings']);
        break;
      case 'help':
        this.router.navigate(['/app/help']);
        break;
      case 'logout':
        this.logout();
        break;
    }
  }

  logout(): void {
    this.authService.logout();
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

  formatDate(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Date(date).toLocaleDateString();
  }
}
