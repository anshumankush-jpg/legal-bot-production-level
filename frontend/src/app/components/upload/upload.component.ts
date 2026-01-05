import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatProgressBarModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule
  ],
  template: `
    <div class="upload-container">
      <mat-card class="upload-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>cloud_upload</mat-icon>
            Upload Documents
          </mat-card-title>
          <mat-card-subtitle>Upload PDFs, text files, or images for indexing</mat-card-subtitle>
        </mat-card-header>
        
        <mat-card-content>
          <div class="upload-section">
            <input
              type="file"
              #fileInput
              (change)="onFileSelected($event)"
              accept=".pdf,.txt,.jpg,.jpeg,.png"
              style="display: none"
            />
            
            <div class="upload-area" (click)="fileInput.click()" [class.dragover]="isDragging">
              <mat-icon class="upload-icon">cloud_upload</mat-icon>
              <p>Click to select or drag and drop files here</p>
              <p class="file-types">Supported: PDF, TXT, JPG, PNG</p>
            </div>
            
            <div *ngIf="selectedFile" class="file-info">
              <mat-icon>description</mat-icon>
              <span>{{ selectedFile.name }}</span>
              <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
            </div>
            
            <div class="form-fields">
              <mat-form-field appearance="outline">
                <mat-label>Organization</mat-label>
                <input matInput [(ngModel)]="organization" placeholder="e.g., PEI Government">
              </mat-form-field>
              
              <mat-form-field appearance="outline">
                <mat-label>Subject</mat-label>
                <input matInput [(ngModel)]="subject" placeholder="e.g., Highway Traffic Act">
              </mat-form-field>
            </div>
            
            <div *ngIf="uploadProgress > 0 && uploadProgress < 100" class="progress-section">
              <mat-progress-bar mode="determinate" [value]="uploadProgress"></mat-progress-bar>
              <p>Uploading: {{ uploadProgress }}%</p>
            </div>
            
            <div *ngIf="uploadResult" class="result-message" [ngClass]="uploadResult.success ? 'success' : 'error'">
              <mat-icon>{{ uploadResult.success ? 'check_circle' : 'error' }}</mat-icon>
              <p>{{ uploadResult.message }}</p>
              <p *ngIf="uploadResult.docId" class="doc-id">Document ID: {{ uploadResult.docId }}</p>
            </div>
            
            <!-- OCR Partial Parse Warning -->
            <div *ngIf="ocrWarning" class="ocr-warning">
              <mat-icon>warning</mat-icon>
              <div class="warning-content">
                <p class="warning-title">We had trouble reading parts of this image</p>
                <p class="warning-text">The image quality may be low (low light, blur, or angle). Please check the extracted text below and correct it if needed.</p>
                <mat-form-field appearance="outline" class="ocr-text-field">
                  <mat-label>Extracted Text (Please Review)</mat-label>
                  <textarea 
                    matInput 
                    [(ngModel)]="ocrExtractedText" 
                    rows="6"
                    placeholder="OCR extracted text will appear here..."
                  ></textarea>
                </mat-form-field>
                <button mat-button (click)="retryOCR()" class="retry-button">
                  <mat-icon>refresh</mat-icon>
                  Retry OCR
                </button>
              </div>
            </div>
            
            <button
              mat-raised-button
              color="primary"
              (click)="uploadFile()"
              [disabled]="!selectedFile || isUploading"
              class="upload-button"
            >
              <mat-icon>upload</mat-icon>
              Upload Document
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .upload-container {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    .upload-card {
      padding: 2rem;
    }
    
    .upload-section {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    
    .upload-area {
      border: 2px dashed #667eea;
      border-radius: 8px;
      padding: 3rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s;
      background: #f9f9f9;
    }
    
    .upload-area:hover {
      background: #f0f0f0;
      border-color: #764ba2;
    }
    
    .upload-area.dragover {
      background: #e8e8ff;
      border-color: #667eea;
    }
    
    .upload-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      color: #667eea;
      margin-bottom: 1rem;
    }
    
    .file-types {
      font-size: 0.875rem;
      color: #666;
      margin-top: 0.5rem;
    }
    
    .file-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 6px;
    }
    
    .file-size {
      color: #666;
      font-size: 0.875rem;
    }
    
    .form-fields {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
    
    .progress-section {
      margin-top: 1rem;
    }
    
    .result-message {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem;
      border-radius: 6px;
    }
    
    .result-message.success {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    .result-message.error {
      background: #ffebee;
      color: #c62828;
    }
    
    .doc-id {
      font-family: monospace;
      font-size: 0.875rem;
      margin-top: 0.5rem;
    }
    
    .upload-button {
      margin-top: 1rem;
    }

    .ocr-warning {
      margin-top: 1rem;
      padding: 1rem;
      background: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 8px;
      display: flex;
      gap: 1rem;
    }

    .ocr-warning mat-icon {
      color: #ff9800;
      flex-shrink: 0;
    }

    .warning-content {
      flex: 1;
    }

    .warning-title {
      font-weight: 600;
      color: #856404;
      margin-bottom: 0.5rem;
    }

    .warning-text {
      color: #856404;
      margin-bottom: 1rem;
      font-size: 0.9rem;
    }

    .ocr-text-field {
      width: 100%;
      margin-bottom: 0.5rem;
    }

    .retry-button {
      color: #856404;
    }
  `]
})
export class UploadComponent {
  selectedFile: File | null = null;
  organization: string = '';
  subject: string = '';
  uploadProgress: number = 0;
  isUploading: boolean = false;
  isDragging: boolean = false;
  uploadResult: any = null;
  ocrWarning: boolean = false;
  ocrExtractedText: string = '';
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.uploadResult = null;
    }
  }

  uploadFile(): void {
    if (!this.selectedFile) {
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;
    this.uploadResult = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile);
    if (this.organization) {
      formData.append('organization', this.organization);
    }
    if (this.subject) {
      formData.append('subject', this.subject);
    }

    const fileExt = this.selectedFile.name.split('.').pop()?.toLowerCase();
    let endpoint = '/api/ingest/file';
    
    if (fileExt && ['jpg', 'jpeg', 'png'].includes(fileExt)) {
      endpoint = '/api/ingest/image';
    }

    this.http.post(`${this.apiUrl}${endpoint}`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * event.loaded / event.total);
        } else if (event.type === HttpEventType.Response) {
          const responseBody = event.body as any;
          
          // Check for OCR warnings or partial parsing
          if (responseBody?.ocr_warning || responseBody?.partial_parse) {
            this.ocrWarning = true;
            this.ocrExtractedText = responseBody?.extracted_text || responseBody?.ocr_text || '';
          }
          
          this.uploadResult = {
            success: true,
            message: 'Document uploaded and indexed successfully!',
            docId: responseBody?.['doc_id']
          };
          this.isUploading = false;
          
          // Don't clear file if OCR warning - let user review
          if (!this.ocrWarning) {
            this.selectedFile = null;
            this.organization = '';
            this.subject = '';
          }
        }
      },
      error: (error) => {
        this.uploadResult = {
          success: false,
          message: error.error?.detail || 'Upload failed. Please try again.'
        };
        this.isUploading = false;
        this.uploadProgress = 0;
        this.ocrWarning = false;
      }
    });
  }

  retryOCR(): void {
    if (this.selectedFile) {
      this.ocrWarning = false;
      this.ocrExtractedText = '';
      this.uploadFile();
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}

