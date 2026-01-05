import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Chart, registerables } from 'chart.js';
import { environment } from '../../../environments/environment';

Chart.register(...registerables);

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressBarModule
  ],
  template: `
    <div class="analytics-container">
      <h2>Analytics Dashboard</h2>
      
      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-header">
              <mat-icon>people</mat-icon>
              <h3>Unique Users</h3>
            </div>
            <p class="stat-value">{{ analyticsSummary?.unique_users_by_day ? getTotalUsers() : 0 }}</p>
            <p class="stat-label">Last 30 days</p>
          </mat-card-content>
        </mat-card>
        
        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-header">
              <mat-icon>message</mat-icon>
              <h3>Total Messages</h3>
            </div>
            <p class="stat-value">{{ analyticsSummary?.messages_by_day ? getTotalMessages() : 0 }}</p>
            <p class="stat-label">Last 30 days</p>
          </mat-card-content>
        </mat-card>
        
        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-header">
              <mat-icon>thumb_up</mat-icon>
              <h3>Positive Feedback</h3>
            </div>
            <p class="stat-value">{{ getPositiveFeedback() }}%</p>
            <p class="stat-label">Based on {{ analyticsSummary?.total_feedback || 0 }} responses</p>
          </mat-card-content>
        </mat-card>
        
        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-header">
              <mat-icon>search</mat-icon>
              <h3>Total Queries</h3>
            </div>
            <p class="stat-value">{{ analyticsSummary?.total_queries || 0 }}</p>
            <p class="stat-label">All time</p>
          </mat-card-content>
        </mat-card>
      </div>
      
      <div class="charts-grid">
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>Users by Day</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <canvas #usersChart></canvas>
          </mat-card-content>
        </mat-card>
        
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>Messages by Day</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <canvas #messagesChart></canvas>
          </mat-card-content>
        </mat-card>
      </div>
      
      <div class="tables-grid">
        <mat-card class="table-card">
          <mat-card-header>
            <mat-card-title>Top Cited Documents</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Citations</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let doc of topCitations">
                  <td>{{ doc.source }}</td>
                  <td>{{ doc.count }}</td>
                </tr>
                <tr *ngIf="topCitations.length === 0">
                  <td colspan="2" class="no-data">No citations yet</td>
                </tr>
              </tbody>
            </table>
          </mat-card-content>
        </mat-card>
        
        <mat-card class="table-card">
          <mat-card-header>
            <mat-card-title>Confidence Distribution</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="confidence-bars">
              <div class="confidence-item">
                <span>High</span>
                <mat-progress-bar mode="determinate" [value]="getConfidencePercent('high')"></mat-progress-bar>
                <span>{{ confidenceDistribution?.high || 0 }}</span>
              </div>
              <div class="confidence-item">
                <span>Medium</span>
                <mat-progress-bar mode="determinate" [value]="getConfidencePercent('medium')"></mat-progress-bar>
                <span>{{ confidenceDistribution?.medium || 0 }}</span>
              </div>
              <div class="confidence-item">
                <span>Low</span>
                <mat-progress-bar mode="determinate" [value]="getConfidencePercent('low')"></mat-progress-bar>
                <span>{{ confidenceDistribution?.low || 0 }}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .analytics-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    .analytics-container h2 {
      margin-bottom: 2rem;
      color: #333;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .stat-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .stat-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
    
    .stat-header mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
    }
    
    .stat-value {
      font-size: 2.5rem;
      font-weight: bold;
      margin: 0.5rem 0;
    }
    
    .stat-label {
      font-size: 0.875rem;
      opacity: 0.9;
      margin: 0;
    }
    
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    
    .chart-card {
      padding: 1.5rem;
    }
    
    .tables-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 1.5rem;
    }
    
    .data-table {
      width: 100%;
      border-collapse: collapse;
    }
    
    .data-table th {
      text-align: left;
      padding: 0.75rem;
      background: #f5f5f5;
      font-weight: 500;
    }
    
    .data-table td {
      padding: 0.75rem;
      border-bottom: 1px solid #e0e0e0;
    }
    
    .no-data {
      text-align: center;
      color: #999;
      padding: 2rem;
    }
    
    .confidence-bars {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .confidence-item {
      display: grid;
      grid-template-columns: 80px 1fr 60px;
      gap: 1rem;
      align-items: center;
    }
  `]
})
export class AnalyticsComponent implements OnInit {
  analyticsSummary: any = null;
  topCitations: any[] = [];
  confidenceDistribution: any = null;
  private usersChart: Chart | null = null;
  private messagesChart: Chart | null = null;
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadAnalytics();
  }

  loadAnalytics(): void {
    this.http.get(`${this.apiUrl}/api/analytics/summary`).subscribe({
      next: (data: any) => {
        this.analyticsSummary = data;
        this.topCitations = data.top_cited_documents || [];
        this.confidenceDistribution = data.confidence_distribution || {};
        this.createCharts();
      },
      error: (error) => {
        console.error('Error loading analytics:', error);
      }
    });
  }

  createCharts(): void {
    if (!this.analyticsSummary) return;

    // Users chart
    const usersData = this.analyticsSummary.unique_users_by_day || {};
    const usersLabels = Object.keys(usersData).reverse();
    const usersValues = Object.values(usersData).reverse();

    // Messages chart
    const messagesData = this.analyticsSummary.messages_by_day || {};
    const messagesLabels = Object.keys(messagesData).reverse();
    const messagesValues = Object.values(messagesData).reverse();

    // Create charts (simplified - you'd use Chart.js here)
    // For now, we'll just display the data
  }

  getTotalUsers(): number {
    if (!this.analyticsSummary?.unique_users_by_day) return 0;
    return Object.values(this.analyticsSummary.unique_users_by_day).reduce((sum: number, val: any) => sum + val, 0);
  }

  getTotalMessages(): number {
    if (!this.analyticsSummary?.messages_by_day) return 0;
    return Object.values(this.analyticsSummary.messages_by_day).reduce((sum: number, val: any) => sum + val, 0);
  }

  getPositiveFeedback(): number {
    if (!this.analyticsSummary?.feedback_percentages) return 0;
    return Math.round(this.analyticsSummary.feedback_percentages.positive || 0);
  }

  getConfidencePercent(level: string): number {
    if (!this.confidenceDistribution) return 0;
    const total = (this.confidenceDistribution.high || 0) + 
                  (this.confidenceDistribution.medium || 0) + 
                  (this.confidenceDistribution.low || 0);
    if (total === 0) return 0;
    return ((this.confidenceDistribution[level] || 0) / total) * 100;
  }
}

