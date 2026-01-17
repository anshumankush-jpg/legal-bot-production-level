import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

// Simple UUID generator
function uuidv4(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: any[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

@Injectable({
  providedIn: 'root'
})
export class ChatStoreService {
  private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
  private activeConversationIdSubject = new BehaviorSubject<string | null>(null);
  private isTypingSubject = new BehaviorSubject<boolean>(false);

  conversations$ = this.conversationsSubject.asObservable();
  activeConversationId$ = this.activeConversationIdSubject.asObservable();
  isTyping$ = this.isTypingSubject.asObservable();

  constructor() {
    this.loadConversations();
  }

  private loadConversations(): void {
    const saved = localStorage.getItem('legid_conversations');
    if (saved) {
      try {
        const conversations = JSON.parse(saved);
        // Convert date strings back to Date objects
        conversations.forEach((conv: Conversation) => {
          conv.createdAt = new Date(conv.createdAt);
          conv.updatedAt = new Date(conv.updatedAt);
          conv.messages.forEach(msg => {
            msg.timestamp = new Date(msg.timestamp);
          });
        });
        this.conversationsSubject.next(conversations);
      } catch (e) {
        console.error('Failed to load conversations', e);
      }
    }
  }

  private saveConversations(): void {
    const conversations = this.conversationsSubject.value;
    localStorage.setItem('legid_conversations', JSON.stringify(conversations));
  }

  getConversations(): Conversation[] {
    return this.conversationsSubject.value;
  }

  getActiveConversation(): Conversation | null {
    const activeId = this.activeConversationIdSubject.value;
    if (!activeId) return null;
    return this.conversationsSubject.value.find(c => c.id === activeId) || null;
  }

  createConversation(): string {
    const newConv: Conversation = {
      id: uuidv4(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    const conversations = [newConv, ...this.conversationsSubject.value];
    this.conversationsSubject.next(conversations);
    this.activeConversationIdSubject.next(newConv.id);
    this.saveConversations();
    
    return newConv.id;
  }

  setActiveConversation(id: string): void {
    this.activeConversationIdSubject.next(id);
  }

  addMessage(conversationId: string, content: string, role: 'user' | 'assistant'): void {
    const conversations = this.conversationsSubject.value;
    const conv = conversations.find(c => c.id === conversationId);
    
    if (!conv) return;

    const message: Message = {
      id: uuidv4(),
      role,
      content,
      timestamp: new Date()
    };

    conv.messages.push(message);
    conv.updatedAt = new Date();

    // Update title based on first user message
    if (conv.messages.length === 1 && role === 'user') {
      conv.title = content.substring(0, 50) + (content.length > 50 ? '...' : '');
    }

    this.conversationsSubject.next([...conversations]);
    this.saveConversations();
  }

  async sendMessage(conversationId: string, content: string): Promise<void> {
    console.log('🔵 ChatStoreService.sendMessage called');
    console.log('   conversationId:', conversationId);
    console.log('   content:', content);
    
    // Add user message
    this.addMessage(conversationId, content, 'user');
    console.log('✅ User message added');

    // Show typing indicator
    this.isTypingSubject.next(true);
    console.log('⏳ Typing indicator ON');

    // Simulate API call
    const delay = 1500 + Math.random() * 1000;
    console.log('⏰ Waiting', delay, 'ms for response...');
    await new Promise(resolve => setTimeout(resolve, delay));

    // Generate mock response
    const response = this.generateMockResponse(content);
    console.log('📝 Generated response:', response.substring(0, 100) + '...');
    
    this.addMessage(conversationId, response, 'assistant');
    console.log('✅ Assistant message added');

    // Hide typing indicator
    this.isTypingSubject.next(false);
    console.log('⏳ Typing indicator OFF');
  }

  private generateMockResponse(userMessage: string): string {
    const responses = [
      `**TITLE: LEGAL RESPONSE TO YOUR INQUIRY**

**EXECUTIVE SUMMARY**

• I've analyzed your question regarding "${userMessage.substring(0, 30)}..."
• Based on Canadian law and relevant statutes, here's what you need to know.

**DETAILED ANALYSIS**

1. **Legal Framework**
   Your situation falls under several areas of law including contract law, civil procedure, and statutory regulations.

2. **Your Options**
   • Option A: Proceed with formal legal action
   • Option B: Attempt mediation or alternative dispute resolution
   • Option C: Seek settlement negotiations

3. **Important Considerations**
   Please note that this is general legal information. For advice specific to your case, consult with a licensed lawyer in your jurisdiction.

**NEXT STEPS**

Contact a legal professional to discuss your specific circumstances and determine the best course of action.`,
      
      `**GREETING AND INITIAL ENGAGEMENT**

Thank you for your question about ${userMessage.substring(0, 30)}...

**EXECUTIVE SUMMARY**

• Acknowledging your inquiry
• Ready to assist with any legal questions or topics you have in mind
• This platform provides general legal information for educational purposes

**KEY POINTS**

Based on your question, I can help you understand:
1. The relevant legal principles
2. Your potential options
3. Important considerations

**DISCLAIMER**

This is general information only, not legal advice. For advice about your specific case, consult a licensed lawyer or paralegal.`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }

  deleteConversation(id: string): void {
    const conversations = this.conversationsSubject.value.filter(c => c.id !== id);
    this.conversationsSubject.next(conversations);
    
    if (this.activeConversationIdSubject.value === id) {
      this.activeConversationIdSubject.next(conversations[0]?.id || null);
    }
    
    this.saveConversations();
  }

  searchConversations(query: string): Conversation[] {
    if (!query.trim()) {
      return this.conversationsSubject.value;
    }

    const lowerQuery = query.toLowerCase();
    return this.conversationsSubject.value.filter(conv =>
      conv.title.toLowerCase().includes(lowerQuery) ||
      conv.messages.some(msg => msg.content.toLowerCase().includes(lowerQuery))
    );
  }
}
