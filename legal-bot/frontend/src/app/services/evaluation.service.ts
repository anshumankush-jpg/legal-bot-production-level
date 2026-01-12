import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, forkJoin } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { ChatService } from './chat.service';

export interface EvaluationTestCase {
  id: string;
  description?: string;
  jurisdiction: string;
  ticket_data: {
    offence_code?: string;
    offence_description?: string;
    fine_amount?: number;
    demerit_points?: number;
  };
  question: string;
  expected_output: {
    must_include?: string[];
    must_not_include?: string[];
    offence_identified?: boolean;
    demerit_points_correct?: boolean;
    options_presented?: boolean;
    consequences_explained?: boolean;
    process_explained?: boolean;
    deadline_mentioned?: boolean;
  };
}

export interface EvaluationResult {
  testCaseId: string;
  passed: boolean;
  failures: string[];
  actualAnswer: string;
  actualMetadata?: any;
  responseTime?: number;
}

@Injectable({
  providedIn: 'root'
})
export class EvaluationService {
  private apiUrl = environment.apiUrl;
  
  // Hard-coded test cases matching evaluation/test_cases/ontario_tickets.json
  private testCases: EvaluationTestCase[] = [
    {
      id: 'test_001',
      description: 'Speeding ticket - 45 km/h in 30 km/h zone',
      jurisdiction: 'Ontario',
      ticket_data: {
        offence_code: 'HTA 128(1)',
        offence_description: 'Speeding - 45 km/h in a 30 km/h zone',
        fine_amount: 95.00,
        demerit_points: 3
      },
      question: 'What are my options for this ticket?',
      expected_output: {
        must_include: [
          '3 demerit points',
          'fine of $95',
          'Option 1: Fight',
          'Option 2: Pay',
          '15 days to dispute',
          'disclaimer'
        ],
        must_not_include: [
          'guarantee',
          'you will win'
        ],
        offence_identified: true,
        demerit_points_correct: true,
        options_presented: true
      }
    },
    {
      id: 'test_002',
      description: 'Red light violation - consequences',
      jurisdiction: 'Ontario',
      ticket_data: {
        offence_code: 'HTA 144(18)',
        offence_description: 'Fail to stop at red light',
        fine_amount: 200.00,
        demerit_points: 3
      },
      question: 'What happens if I get 3 demerit points?',
      expected_output: {
        must_include: [
          '3 demerit points',
          'insurance impact',
          'minor increase',
          'disclaimer'
        ],
        offence_identified: true,
        consequences_explained: true
      }
    },
    {
      id: 'test_003',
      description: 'Distracted driving - fight process',
      jurisdiction: 'Ontario',
      ticket_data: {
        offence_code: 'HTA 78.1(1)',
        offence_description: 'Distracted driving - using handheld device',
        fine_amount: 615.00,
        demerit_points: 3
      },
      question: 'How do I fight this ticket?',
      expected_output: {
        must_include: [
          'request disclosure',
          'file trial request',
          '15 days deadline',
          'disclaimer'
        ],
        process_explained: true,
        deadline_mentioned: true
      }
    }
  ];

  constructor(
    private http: HttpClient,
    private chatService: ChatService
  ) {}

  /**
   * Get all test cases
   */
  getTestCases(): EvaluationTestCase[] {
    return this.testCases;
  }

  /**
   * Run a single test case
   */
  runTestCase(testCase: EvaluationTestCase): Observable<EvaluationResult> {
    const startTime = Date.now();
    
    // Build context from ticket data
    const ticketContext = this.buildTicketContext(testCase.ticket_data);
    const fullQuestion = ticketContext ? `${ticketContext}\n\n${testCase.question}` : testCase.question;
    
    return this.chatService.askQuestion({ question: fullQuestion }).pipe(
      map(response => {
        const responseTime = Date.now() - startTime;
        const result = this.evaluateResponse(testCase, response.answer, responseTime);
        return result;
      }),
      catchError(error => {
        const responseTime = Date.now() - startTime;
        return of({
          testCaseId: testCase.id,
          passed: false,
          failures: [`Error: ${error.message || 'Unknown error'}`],
          actualAnswer: 'Error occurred while processing query',
          responseTime
        });
      })
    );
  }

  /**
   * Run all test cases
   */
  runAllTests(): Observable<EvaluationResult[]> {
    const testObservables = this.testCases.map(testCase => 
      this.runTestCase(testCase)
    );
    
    return forkJoin(testObservables);
  }

  /**
   * Build ticket context string from ticket data
   */
  private buildTicketContext(ticketData: EvaluationTestCase['ticket_data']): string {
    const parts: string[] = [];
    
    if (ticketData.offence_code) {
      parts.push(`Offence Code: ${ticketData.offence_code}`);
    }
    if (ticketData.offence_description) {
      parts.push(`Offence: ${ticketData.offence_description}`);
    }
    if (ticketData.fine_amount) {
      parts.push(`Fine: $${ticketData.fine_amount.toFixed(2)}`);
    }
    if (ticketData.demerit_points !== undefined) {
      parts.push(`Demerit Points: ${ticketData.demerit_points}`);
    }
    
    return parts.length > 0 
      ? `Ticket Information:\n${parts.join('\n')}`
      : '';
  }

  /**
   * Evaluate response against expected output
   */
  private evaluateResponse(
    testCase: EvaluationTestCase,
    actualAnswer: string,
    responseTime: number
  ): EvaluationResult {
    const failures: string[] = [];
    const answerLower = actualAnswer.toLowerCase();
    const expected = testCase.expected_output;

    // Check must_include phrases
    if (expected.must_include) {
      for (const phrase of expected.must_include) {
        if (!answerLower.includes(phrase.toLowerCase())) {
          failures.push(`Missing required phrase: "${phrase}"`);
        }
      }
    }

    // Check must_not_include phrases
    if (expected.must_not_include) {
      for (const phrase of expected.must_not_include) {
        if (answerLower.includes(phrase.toLowerCase())) {
          failures.push(`Contains forbidden phrase: "${phrase}"`);
        }
      }
    }

    // Check offence identification
    if (expected.offence_identified) {
      const offenceCode = testCase.ticket_data.offence_code;
      const offenceDesc = testCase.ticket_data.offence_description;
      
      if (offenceCode && !answerLower.includes(offenceCode.toLowerCase())) {
        if (offenceDesc && !answerLower.includes(offenceDesc.toLowerCase().split(' ')[0])) {
          failures.push('Offence not clearly identified');
        }
      }
    }

    // Check demerit points
    if (expected.demerit_points_correct) {
      const expectedPoints = testCase.ticket_data.demerit_points;
      if (expectedPoints !== undefined) {
        const pointsRegex = new RegExp(`\\b${expectedPoints}\\s*(demerit|point)`, 'i');
        if (!pointsRegex.test(actualAnswer)) {
          failures.push(`Demerit points (${expectedPoints}) not correctly stated`);
        }
      }
    }

    // Check options presented
    if (expected.options_presented) {
      const hasFight = /option\s*1|fight|dispute|appeal|trial/i.test(answerLower);
      const hasPay = /option\s*2|pay|payment|fine/i.test(answerLower);
      
      if (!hasFight) {
        failures.push('Fight/dispute option not mentioned');
      }
      if (!hasPay) {
        failures.push('Pay option not mentioned');
      }
    }

    // Check disclaimer
    if (!answerLower.includes('disclaimer') && 
        !answerLower.includes('not legal advice') &&
        !answerLower.includes('general information')) {
      failures.push('Disclaimer not present');
    }

    // Check consequences explained
    if (expected.consequences_explained) {
      const hasConsequences = /consequence|impact|effect|insurance|licen[cs]e/i.test(answerLower);
      if (!hasConsequences) {
        failures.push('Consequences not explained');
      }
    }

    // Check process explained
    if (expected.process_explained) {
      const hasProcess = /process|step|how to|procedure|file|request/i.test(answerLower);
      if (!hasProcess) {
        failures.push('Fight process not explained');
      }
    }

    // Check deadline mentioned
    if (expected.deadline_mentioned) {
      const hasDeadline = /\d+\s*day|deadline|time limit|must.*within/i.test(answerLower);
      if (!hasDeadline) {
        failures.push('Deadline not mentioned');
      }
    }

    return {
      testCaseId: testCase.id,
      passed: failures.length === 0,
      failures,
      actualAnswer,
      responseTime
    };
  }
}

