import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule
  ],
  template: `
    <div class="documents-container">
      <h2>Document Library</h2>
      
      <mat-card class="filter-card">
        <mat-card-content>
          <div class="filters">
            <mat-form-field appearance="outline">
              <mat-label>Organization</mat-label>
              <input matInput [(ngModel)]="filterOrganization" (ngModelChange)="loadDocuments()">
            </mat-form-field>
            
            <mat-form-field appearance="outline">
              <mat-label>Subject</mat-label>
              <input matInput [(ngModel)]="filterSubject" (ngModelChange)="loadDocuments()">
            </mat-form-field>
            
            <mat-form-field appearance="outline">
              <mat-label>Type</mat-label>
              <input matInput [(ngModel)]="filterType" (ngModelChange)="loadDocuments()">
            </mat-form-field>
          </div>
        </mat-card-content>
      </mat-card>
      
      <mat-card>
        <mat-card-content>
          <table mat-table [dataSource]="documents" class="documents-table">
            <ng-container matColumnDef="source_name">
              <th mat-header-cell *matHeaderCellDef>Document Name</th>
              <td mat-cell *matCellDef="let doc">
                <mat-icon>{{ getTypeIcon(doc.source_type) }}</mat-icon>
                {{ doc.source_name }}
              </td>
            </ng-container>
            
            <ng-container matColumnDef="source_type">
              <th mat-header-cell *matHeaderCellDef>Type</th>
              <td mat-cell *matCellDef="let doc">{{ doc.source_type }}</td>
            </ng-container>
            
            <ng-container matColumnDef="organization">
              <th mat-header-cell *matHeaderCellDef>Organization</th>
              <td mat-cell *matCellDef="let doc">{{ doc.organization || '-' }}</td>
            </ng-container>
            
            <ng-container matColumnDef="subject">
              <th mat-header-cell *matHeaderCellDef>Subject</th>
              <td mat-cell *matCellDef="let doc">{{ doc.subject || '-' }}</td>
            </ng-container>
            
            <ng-container matColumnDef="chunk_count">
              <th mat-header-cell *matHeaderCellDef>Chunks</th>
              <td mat-cell *matCellDef="let doc">{{ doc.chunk_count || 0 }}</td>
            </ng-container>
            
            <ng-container matColumnDef="created_at">
              <th mat-header-cell *matHeaderCellDef>Created</th>
              <td mat-cell *matCellDef="let doc">{{ doc.created_at | date:'short' }}</td>
            </ng-container>
            
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let doc">
                <button mat-icon-button (click)="deleteDocument(doc.doc_id)" color="warn">
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>
            
            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
          
          <div *ngIf="documents.length === 0" class="no-documents">
            <mat-icon>folder_open</mat-icon>
            <p>No documents found</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .documents-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    .filter-card {
      margin-bottom: 2rem;
    }
    
    .filters {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }
    
    .documents-table {
      width: 100%;
    }
    
    .no-documents {
      text-align: center;
      padding: 3rem;
      color: #999;
    }
    
    .no-documents mat-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      margin-bottom: 1rem;
    }
  `]
})
export class DocumentsComponent implements OnInit {
  documents: any[] = [];
  displayedColumns = ['source_name', 'source_type', 'organization', 'subject', 'chunk_count', 'created_at', 'actions'];
  filterOrganization: string = '';
  filterSubject: string = '';
  filterType: string = '';
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    const params: any = {};
    if (this.filterOrganization) params.organization = this.filterOrganization;
    if (this.filterSubject) params.subject = this.filterSubject;
    if (this.filterType) params.source_type = this.filterType;

    this.http.get(`${this.apiUrl}/api/documents`, { params }).subscribe({
      next: (data: any) => {
        this.documents = data.documents || [];
      },
      error: (error) => {
        console.error('Error loading documents:', error);
      }
    });
  }

  deleteDocument(docId: string): void {
    if (confirm('Are you sure you want to delete this document?')) {
      this.http.delete(`${this.apiUrl}/api/documents/${docId}`).subscribe({
        next: () => {
          this.loadDocuments();
        },
        error: (error) => {
          console.error('Error deleting document:', error);
          alert('Failed to delete document');
        }
      });
    }
  }

  getTypeIcon(type: string): string {
    switch (type) {
      case 'pdf': return 'picture_as_pdf';
      case 'image': return 'image';
      case 'text': return 'description';
      default: return 'insert_drive_file';
    }
  }
}

