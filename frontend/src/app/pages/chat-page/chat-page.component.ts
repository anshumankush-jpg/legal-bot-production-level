import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatStoreService, Conversation } from '../../services/chat-store.service';
import { MessageListComponent } from '../../components/chat/message-list.component';
import { ComposerComponent } from '../../components/chat/composer.component';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [CommonModule, MessageListComponent, ComposerComponent],
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss']
})
export class ChatPageComponent implements OnInit, OnDestroy {
  conversation: Conversation | null = null;
  isTyping = false;
  private subscriptions: Subscription[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chatStore: ChatStoreService
  ) {}

  ngOnInit(): void {
    // Subscribe to route params
    const routeSub = this.route.params.subscribe(params => {
      const conversationId = params['id'];
      if (conversationId) {
        this.chatStore.setActiveConversation(conversationId);
        this.loadConversation();
      } else {
        // No conversation ID - check if there's an active conversation or create one
        this.ensureActiveConversation();
      }
    });
    this.subscriptions.push(routeSub);

    // Subscribe to conversation changes
    const convSub = this.chatStore.conversations$.subscribe(() => {
      this.loadConversation();
    });
    this.subscriptions.push(convSub);

    // Subscribe to typing indicator
    const typingSub = this.chatStore.isTyping$.subscribe(typing => {
      this.isTyping = typing;
    });
    this.subscriptions.push(typingSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private ensureActiveConversation(): void {
    // Check if there's already an active conversation
    let activeConv = this.chatStore.getActiveConversation();
    
    if (!activeConv) {
      // Check if there are any existing conversations
      const conversations = this.chatStore.getConversations();
      if (conversations.length > 0) {
        // Use the first (most recent) conversation
        this.chatStore.setActiveConversation(conversations[0].id);
        activeConv = conversations[0];
      } else {
        // No conversations exist - create a new one
        const newId = this.chatStore.createConversation();
        activeConv = this.chatStore.getActiveConversation();
      }
    }
    
    this.conversation = activeConv;
  }

  private loadConversation(): void {
    this.conversation = this.chatStore.getActiveConversation();
    
    // If no conversation loaded, ensure one exists
    if (!this.conversation) {
      this.ensureActiveConversation();
    }
  }

  async handleSendMessage(content: string): Promise<void> {
    console.log('📨 handleSendMessage called with:', content);
    console.log('📋 Current conversation:', this.conversation);
    
    // If no conversation, create one first
    if (!this.conversation) {
      console.log('🆕 No conversation, creating new one...');
      const newId = this.chatStore.createConversation();
      this.conversation = this.chatStore.getActiveConversation();
      console.log('✅ New conversation created:', this.conversation);
    }
    
    if (this.conversation) {
      console.log('📤 Sending message to conversation:', this.conversation.id);
      await this.chatStore.sendMessage(this.conversation.id, content);
      console.log('✅ Message sent!');
    } else {
      console.error('❌ No conversation available!');
    }
  }
}
