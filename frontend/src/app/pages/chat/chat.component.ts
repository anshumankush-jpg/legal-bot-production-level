import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ChatService, ChatMessage } from '../../services/chat.service';
import { UploadService } from '../../services/upload.service';
import { UserContextService } from '../../services/user-context.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') chatContainer!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef;
  @ViewChild('imageInput') imageInput!: ElementRef;
  @ViewChild('cameraInput') cameraInput!: ElementRef;

  messages: ChatMessage[] = [];
  currentMessage: string = '';
  isLoading: boolean = false;
  showUploadMenu: boolean = false;
  uploadProgress: number = 0;
  isUploading: boolean = false;

  constructor(
    private chatService: ChatService,
    private uploadService: UploadService,
    private userContext: UserContextService
  ) {}

  ngOnInit(): void {
    // Add greeting message
    this.messages.push({
      role: 'assistant',
      content: "Hi, I'm your Legal AI. Upload your ticket/summons or ask a question.",
      timestamp: new Date()
    });
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  toggleUploadMenu(): void {
    this.showUploadMenu = !this.showUploadMenu;
  }

  openFileUpload(): void {
    this.fileInput.nativeElement.click();
    this.showUploadMenu = false;
  }

  openImageUpload(): void {
    this.imageInput.nativeElement.click();
    this.showUploadMenu = false;
  }

  openCamera(): void {
    if (this.isMobile()) {
      this.cameraInput.nativeElement.click();
      this.showUploadMenu = false;
    }
  }

  isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.uploadFile(input.files[0]);
    }
  }

  onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.uploadImage(input.files[0]);
    }
  }

  onEnterKey(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  uploadFile(file: File): void {
    this.isUploading = true;
    this.uploadProgress = 0;
    
    const preferences = this.userContext.getPreferences();
    const userId = 'default_user'; // Could be from auth service
    const offenceNumber = preferences?.offenceNumber;
    
    this.uploadService.uploadFile(file, userId, offenceNumber).subscribe({
      next: (result) => {
        this.uploadProgress = result.progress;
        if (result.docId) {
          this.userContext.addRecentDocId(result.docId);
          this.isUploading = false;
          this.addSystemMessage(`Document "${file.name}" uploaded and indexed. Ask me questions now.`);
        }
      },
      error: (error) => {
        this.isUploading = false;
        const errorMsg = error.error?.detail || error.message || 'Upload failed';
        this.addSystemMessage(`Upload failed: ${errorMsg}`);
        console.error('Upload error:', error);
      }
    });
  }

  uploadImage(file: File): void {
    this.isUploading = true;
    this.uploadProgress = 0;
    
    const preferences = this.userContext.getPreferences();
    const userId = 'default_user'; // Could be from auth service
    const offenceNumber = preferences?.offenceNumber;
    
    this.uploadService.uploadImage(file, userId, offenceNumber).subscribe({
      next: (result) => {
        this.uploadProgress = result.progress;
        if (result.docId) {
          this.userContext.addRecentDocId(result.docId);
          this.isUploading = false;
          this.addSystemMessage(`Image "${file.name}" processed. Ask me questions now.`);
        }
      },
      error: (error) => {
        this.isUploading = false;
        const errorMsg = error.error?.detail || error.message || 'Upload failed';
        this.addSystemMessage(`Upload failed: ${errorMsg}`);
        console.error('Upload error:', error);
      }
    });
  }

  addSystemMessage(content: string): void {
    this.messages.push({
      role: 'assistant',
      content,
      timestamp: new Date()
    });
  }

  sendMessage(): void {
    if (!this.currentMessage.trim() || this.isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: this.currentMessage,
      timestamp: new Date()
    };

    this.messages.push(userMessage);
    const question = this.currentMessage;
    this.currentMessage = '';
    this.isLoading = true;

    this.chatService.sendMessage(question).subscribe({
      next: (response) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.answer || response.content,
          timestamp: new Date(),
          citations: response.citations,
          structuredData: this.parseStructuredResponse(response.answer || response.content)
        };
        this.messages.push(assistantMessage);
        this.isLoading = false;
      },
      error: (error) => {
        this.messages.push({
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error.error?.message || 'Chat failed'}. Please make sure the backend is running and try again.`,
          timestamp: new Date()
        });
        this.isLoading = false;
      }
    });
  }

  parseStructuredResponse(content: string): any {
    const structured: any = {};
    
    // Extract demerit points
    const demeritMatch = content.match(/[Dd]emerit [Pp]oints?:?\s*(\d+)/);
    if (demeritMatch) {
      structured.demeritPoints = demeritMatch[1];
    }
    
    // Extract consequences (simplified)
    const consequencesMatch = content.match(/[Cc]onsequences?:?\s*([^.]+)/);
    if (consequencesMatch) {
      structured.consequences = consequencesMatch[1].split(',').map(c => c.trim());
    }
    
    return structured;
  }

  formatStructuredResponse(message: ChatMessage): string {
    if (!message.structuredData) {
      return message.content;
    }
    
    let formatted = message.content;
    
    // Add structured sections if detected
    if (message.structuredData.demeritPoints) {
      formatted = `<strong>Demerit Points:</strong> ${message.structuredData.demeritPoints}\n\n` + formatted;
    }
    
    return formatted;
  }
}