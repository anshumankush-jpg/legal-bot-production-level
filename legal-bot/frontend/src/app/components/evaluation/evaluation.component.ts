import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { EvaluationService, EvaluationTestCase, EvaluationResult } from '../../services/evaluation.service';

@Component({
  selector: 'app-evaluation',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatChipsModule,
    MatExpansionModule
  ],
  template: `
    <div class="evaluation-container">
      <div class="evaluation-header">
        <h1>System Evaluation – Ontario Tickets</h1>
        <p class="description">
          This page runs the Ontario test cases against the current backend and compares expected vs actual behavior.
        </p>
      </div>

      <div class="control-bar">
        <button
          mat-raised-button
          color="primary"
          (click)="runAllTests()"
          [disabled]="isRunning"
          class="run-button"
        >
          <mat-icon>{{ isRunning ? 'hourglass_empty' : 'play_arrow' }}</mat-icon>
          {{ isRunning ? 'Running Tests...' : 'Run All Tests' }}
        </button>
        
        <div class="summary" *ngIf="summary.total > 0">
          <span class="summary-item passed">
            <mat-icon>check_circle</mat-icon>
            {{ summary.passed }} passed
          </span>
          <span class="summary-item failed">
            <mat-icon>error</mat-icon>
            {{ summary.failed }} failed
          </span>
          <span class="summary-item total">
            {{ summary.total }} total
          </span>
        </div>
      </div>

      <div class="test-cases">
        <mat-card *ngFor="let testCase of testCases; let i = index" class="test-card">
          <mat-card-header>
            <div class="test-header">
              <div class="test-title">
                <h3>Test #{{ i + 1 }} – {{ testCase.description || testCase.question }}</h3>
                <mat-chip class="jurisdiction-chip">{{ testCase.jurisdiction }}</mat-chip>
              </div>
              <div class="test-status" *ngIf="results[testCase.id]">
                <mat-chip 
                  [class.pass]="results[testCase.id].passed"
                  [class.fail]="!results[testCase.id].passed"
                >
                  <mat-icon>{{ results[testCase.id].passed ? 'check_circle' : 'cancel' }}</mat-icon>
                  {{ results[testCase.id].passed ? 'PASS' : 'FAIL' }}
                </mat-chip>
              </div>
            </div>
          </mat-card-header>

          <mat-card-content>
            <div class="test-sections">
              <!-- Input Section -->
              <div class="section">
                <h4 class="section-title">Input</h4>
                <div class="section-content">
                  <p><strong>Question:</strong> {{ testCase.question }}</p>
                  <div *ngIf="testCase.ticket_data" class="ticket-data">
                    <p><strong>Ticket Data:</strong></p>
                    <ul>
                      <li *ngIf="testCase.ticket_data.offence_code">
                        Offence Code: {{ testCase.ticket_data.offence_code }}
                      </li>
                      <li *ngIf="testCase.ticket_data.offence_description">
                        Offence: {{ testCase.ticket_data.offence_description }}
                      </li>
                      <li *ngIf="testCase.ticket_data.fine_amount">
                        Fine: ${{ testCase.ticket_data.fine_amount.toFixed(2) }}
                      </li>
                      <li *ngIf="testCase.ticket_data.demerit_points !== undefined">
                        Demerit Points: {{ testCase.ticket_data.demerit_points }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Expected Section -->
              <div class="section">
                <h4 class="section-title">Expected</h4>
                <div class="section-content">
                  <ul class="expected-list">
                    <li *ngIf="testCase.expected_output.offence_identified">
                      <mat-icon>check</mat-icon>
                      Offence identified
                    </li>
                    <li *ngIf="testCase.expected_output.demerit_points_correct">
                      <mat-icon>check</mat-icon>
                      Demerit points correct
                    </li>
                    <li *ngIf="testCase.expected_output.options_presented">
                      <mat-icon>check</mat-icon>
                      Both FIGHT and PAY options presented
                    </li>
                    <li *ngIf="testCase.expected_output.consequences_explained">
                      <mat-icon>check</mat-icon>
                      Consequences explained
                    </li>
                    <li *ngIf="testCase.expected_output.process_explained">
                      <mat-icon>check</mat-icon>
                      Fight process explained
                    </li>
                    <li *ngIf="testCase.expected_output.deadline_mentioned">
                      <mat-icon>check</mat-icon>
                      Deadline mentioned
                    </li>
                    <li *ngIf="testCase.expected_output.must_include?.length">
                      <mat-icon>check</mat-icon>
                      Must include: {{ testCase.expected_output.must_include.join(', ') }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Actual Section -->
              <div class="section" *ngIf="results[testCase.id]">
                <h4 class="section-title">Actual</h4>
                <div class="section-content">
                  <div class="failures" *ngIf="results[testCase.id].failures.length > 0">
                    <p class="failures-title">Failures:</p>
                    <ul>
                      <li *ngFor="let failure of results[testCase.id].failures">{{ failure }}</li>
                    </ul>
                  </div>
                  
                  <div class="response-time" *ngIf="results[testCase.id].responseTime">
                    Response time: {{ results[testCase.id].responseTime }}ms
                  </div>

                  <mat-expansion-panel class="answer-panel">
                    <mat-expansion-panel-header>
                      <mat-panel-title>
                        View Model Answer
                      </mat-panel-title>
                    </mat-expansion-panel-header>
                    <div class="actual-answer">
                      {{ results[testCase.id].actualAnswer }}
                    </div>
                  </mat-expansion-panel>
                </div>
              </div>

              <!-- Pending State -->
              <div class="section pending" *ngIf="!results[testCase.id] && !isRunning">
                <p>Not yet run</p>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .evaluation-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
    }

    .evaluation-header {
      margin-bottom: 2rem;
    }

    .evaluation-header h1 {
      color: #0B1F3B; /* $primary-navy */
      margin-bottom: 0.5rem;
    }

    .description {
      color: #757575; /* $text-secondary */
      font-size: 1rem; /* $font-size-base */
    }

    .control-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding: 1rem;
      background: #FFFFFF; /* $background-white */
      border-radius: 12px; /* $radius-lg */
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* $shadow-sm */
    }

    .run-button {
      background-color: #0B1F3B !important; /* $primary-navy */
      color: #FFFFFF !important; /* $text-on-primary */
    }

    .summary {
      display: flex;
      gap: 1.5rem;
      align-items: center;
    }

    .summary-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: $font-weight-medium;
    }

    .summary-item.passed {
      color: #4CAF50; /* $success */
    }

    .summary-item.failed {
      color: #F44336; /* $error */
    }

    .summary-item.total {
      color: #757575; /* $text-secondary */
    }

    .test-cases {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .test-card {
      background: #FFFFFF; /* $background-white */
      border-radius: 12px; /* $radius-lg */
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* $shadow-md */
    }

    .test-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      width: 100%;
    }

    .test-title {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex: 1;
    }

    .test-title h3 {
      margin: 0;
      color: #212121; /* $text-primary */
      font-size: 1.25rem; /* $font-size-xl */
    }

    .jurisdiction-chip {
      background-color: #4DD0E1 !important; /* $accent-teal-light */
      color: #0B1F3B !important; /* $primary-navy */
    }

    .test-status mat-chip.pass {
      background-color: #4CAF50 !important; /* $success */
      color: white !important;
    }

    .test-status mat-chip.fail {
      background-color: #F44336 !important; /* $error */
      color: white !important;
    }

    .test-sections {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .section {
      border-left: 3px solid #00BCD4; /* $accent-teal */
      padding-left: 1rem;
    }

    .section-title {
      color: #0B1F3B; /* $primary-navy */
      font-size: 1.125rem; /* $font-size-lg */
      font-weight: 600; /* $font-weight-semibold */
      margin-bottom: 0.5rem;
    }

    .section-content {
      color: #212121; /* $text-primary */
    }

    .ticket-data {
      margin-top: 0.5rem;
      padding: 0.75rem;
      background: #FAFAFA; /* $surface */
      border-radius: 8px; /* $radius-md */
    }

    .ticket-data ul {
      margin: 0.5rem 0 0 1.5rem;
      list-style-type: disc;
    }

    .expected-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .expected-list li {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
      color: #212121; /* $text-primary */
    }

    .expected-list mat-icon {
      color: #4CAF50; /* $success */
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .failures {
      margin-bottom: 1rem;
      padding: 1rem;
      background: #ffebee;
      border-radius: 8px; /* $radius-md */
      border-left: 3px solid #F44336; /* $error */
    }

    .failures-title {
      font-weight: 600; /* $font-weight-semibold */
      color: #F44336; /* $error */
      margin-bottom: 0.5rem;
    }

    .failures ul {
      margin: 0.5rem 0 0 1.5rem;
      color: #212121; /* $text-primary */
    }

    .response-time {
      margin-bottom: 1rem;
      color: #757575; /* $text-secondary */
      font-size: 0.875rem; /* $font-size-sm */
    }

    .answer-panel {
      margin-top: 1rem;
    }

    .actual-answer {
      padding: 1rem;
      background: #FAFAFA; /* $surface */
      border-radius: 8px; /* $radius-md */
      white-space: pre-wrap;
      line-height: 1.75; /* $line-height-relaxed */
      color: #212121; /* $text-primary */
    }

    .pending {
      color: #757575; /* $text-secondary */
      font-style: italic;
    }

    @media (max-width: 768px) {
      .evaluation-container {
        padding: 1rem;
      }

      .control-bar {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
      }

      .test-header {
        flex-direction: column;
        gap: 1rem;
      }
    }
  `]
})
export class EvaluationComponent implements OnInit {
  testCases: EvaluationTestCase[] = [];
  results: { [id: string]: EvaluationResult } = {};
  isRunning: boolean = false;
  summary = {
    total: 0,
    passed: 0,
    failed: 0
  };

  constructor(private evaluationService: EvaluationService) {}

  ngOnInit(): void {
    this.testCases = this.evaluationService.getTestCases();
    this.summary.total = this.testCases.length;
  }

  runAllTests(): void {
    this.isRunning = true;
    this.results = {};
    this.summary = { total: this.testCases.length, passed: 0, failed: 0 };

    this.evaluationService.runAllTests().subscribe({
      next: (results) => {
        results.forEach(result => {
          this.results[result.testCaseId] = result;
          if (result.passed) {
            this.summary.passed++;
          } else {
            this.summary.failed++;
          }
        });
        this.isRunning = false;
      },
      error: (error) => {
        console.error('Error running tests:', error);
        this.isRunning = false;
      }
    });
  }
}

