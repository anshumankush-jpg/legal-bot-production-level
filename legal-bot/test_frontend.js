#!/usr/bin/env node
/**
 * PLAZA-AI Frontend Testing Suite
 * Comprehensive test suite for Artillery-enabled frontend functionality
 */

// Test configuration
const TEST_CONFIG = {
  backendUrl: 'http://localhost:8000',
  frontendUrl: 'http://localhost:3000',
  testUserId: 'test_user_frontend_' + Date.now(),
  testTimeout: 30000
};

// Test results
const testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  details: []
};

// Helper functions
function logTest(testName, status, message = '') {
  const statusIcon = status ? '✅' : '❌';
  console.log(`${statusIcon} ${testName}: ${message}`);
  testResults.details.push({ testName, status, message });

  if (status) {
    testResults.passed++;
  } else {
    testResults.failed++;
  }
  testResults.total++;
}

async function makeRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      timeout: TEST_CONFIG.testTimeout,
      ...options
    });
    return response;
  } catch (error) {
    throw new Error(`Request failed: ${error.message}`);
  }
}

// Test functions
async function testBackendConnection() {
  console.log('\n🔗 Testing Backend Connection...');

  try {
    const response = await makeRequest(`${TEST_CONFIG.backendUrl}/api/artillery/health`);
    if (response.ok) {
      const data = await response.json();
      logTest('Backend Health Check', true, `Status: ${data.status}, Index size: ${data.faiss_index_size}`);
      return true;
    } else {
      logTest('Backend Health Check', false, `HTTP ${response.status}`);
      return false;
    }
  } catch (error) {
    logTest('Backend Health Check', false, error.message);
    return false;
  }
}

async function testFrontendConnection() {
  console.log('\n🌐 Testing Frontend Connection...');

  try {
    // Since we can't directly test the React app, we'll check if the dev server is running
    const response = await makeRequest(TEST_CONFIG.frontendUrl);
    if (response.ok) {
      logTest('Frontend Dev Server', true, 'Server is responding');
      return true;
    } else {
      logTest('Frontend Dev Server', false, `HTTP ${response.status}`);
      return false;
    }
  } catch (error) {
    logTest('Frontend Dev Server', false, 'Server not accessible - may need to start manually');
    return false;
  }
}

async function testDocumentUpload() {
  console.log('\n📎 Testing Document Upload Endpoint...');

  // Create a test PDF-like file
  const testContent = `
    Ontario Highway Traffic Act
    Offence No: 123456789

    Section 128: Speeding
    (1) Every person who operates a motor vehicle on a highway at a speed greater than the speed limit is guilty of an offence.

    Penalties:
    - For exceeding the speed limit by 1-19 km/h: $5.00 + 2 demerit points
    - For exceeding the speed limit by 20-29 km/h: $12.00 + 3 demerit points
    - For exceeding the speed limit by 30 km/h or more: $25.00 + 4 demerit points
  `;

  const blob = new Blob([testContent], { type: 'application/pdf' });
  const formData = new FormData();
  formData.append('file', blob, 'test_traffic_ticket.pdf');
  formData.append('user_id', TEST_CONFIG.testUserId);

  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/upload`, {
      method: 'POST',
      body: formData,
      timeout: TEST_CONFIG.testTimeout
    });

    if (response.ok) {
      const data = await response.json();
      const hasDocId = data.doc_id && data.doc_id.length > 0;
      const hasChunks = data.chunks_indexed && data.chunks_indexed > 0;
      const hasOffenceNumber = data.detected_offence_number === '123456789';

      if (hasDocId && hasChunks && hasOffenceNumber) {
        logTest('Document Upload', true, `Doc ID: ${data.doc_id}, Chunks: ${data.chunks_indexed}, Offence: ${data.detected_offence_number}`);
        return { docId: data.doc_id, chunks: data.chunks_indexed, offenceNumber: data.detected_offence_number };
      } else {
        logTest('Document Upload', false, `Missing fields: doc_id=${hasDocId}, chunks=${hasChunks}, offence=${hasOffenceNumber}`);
        return null;
      }
    } else {
      const errorText = await response.text();
      logTest('Document Upload', false, `HTTP ${response.status}: ${errorText}`);
      return null;
    }
  } catch (error) {
    logTest('Document Upload', false, error.message);
    return null;
  }
}

async function testChatQuery(offenceNumber = null) {
  console.log('\n💬 Testing Chat Query...');

  const payload = {
    message: "What are the penalties for speeding?",
    offence_number: offenceNumber,
    top_k: 5
  };

  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      timeout: TEST_CONFIG.testTimeout
    });

    if (response.ok) {
      const data = await response.json();
      const hasAnswer = data.answer && data.answer.length > 10;
      const hasCitations = data.citations && Array.isArray(data.citations);
      const hasChunksUsed = typeof data.chunks_used === 'number';
      const hasConfidence = typeof data.confidence === 'number';

      if (hasAnswer && hasCitations && hasChunksUsed && hasConfidence) {
        logTest('Chat Query', true, `Answer: ${data.answer.substring(0, 50)}..., Citations: ${data.citations.length}, Chunks: ${data.chunks_used}, Confidence: ${data.confidence.toFixed(2)}`);
        return data;
      } else {
        logTest('Chat Query', false, `Missing fields: answer=${hasAnswer}, citations=${hasCitations}, chunks=${hasChunksUsed}, confidence=${hasConfidence}`);
        return null;
      }
    } else {
      const errorText = await response.text();
      logTest('Chat Query', false, `HTTP ${response.status}: ${errorText}`);
      return null;
    }
  } catch (error) {
    logTest('Chat Query', false, error.message);
    return null;
  }
}

async function testOffenceNumberFiltering() {
  console.log('\n🎯 Testing Offence Number Filtering...');

  const payload = {
    message: "What are the penalties for this offence?",
    offence_number: "123456789",
    top_k: 5
  };

  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      timeout: TEST_CONFIG.testTimeout
    });

    if (response.ok) {
      const data = await response.json();
      // Check if the response mentions the offence number or is more relevant
      const mentionsOffence = data.answer.toLowerCase().includes('123456789') ||
                             data.answer.toLowerCase().includes('offence');
      const hasRelevantContent = data.answer.length > 20;

      if (mentionsOffence && hasRelevantContent) {
        logTest('Offence Number Filtering', true, 'Response appears to be filtered by offence number');
        return true;
      } else {
        logTest('Offence Number Filtering', false, 'Response may not be properly filtered');
        return false;
      }
    } else {
      logTest('Offence Number Filtering', false, `HTTP ${response.status}`);
      return false;
    }
  } catch (error) {
    logTest('Offence Number Filtering', false, error.message);
    return false;
  }
}

async function testErrorHandling() {
  console.log('\n🚨 Testing Error Handling...');

  // Test with invalid file type
  const invalidFile = new File(['invalid content'], 'test.exe', { type: 'application/octet-stream' });
  const formData = new FormData();
  formData.append('file', invalidFile);
  formData.append('user_id', TEST_CONFIG.testUserId);

  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/upload`, {
      method: 'POST',
      body: formData,
      timeout: TEST_CONFIG.testTimeout
    });

    // Should return an error for invalid file type
    if (response.status === 400 || response.status === 422) {
      logTest('Error Handling - Invalid File', true, 'Properly rejected invalid file type');
    } else if (response.ok) {
      logTest('Error Handling - Invalid File', false, 'Should have rejected invalid file type');
    } else {
      logTest('Error Handling - Invalid File', true, `Proper error response: ${response.status}`);
    }
  } catch (error) {
    logTest('Error Handling - Invalid File', false, error.message);
  }

  // Test with empty query
  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: "" }),
      timeout: TEST_CONFIG.testTimeout
    });

    if (response.status === 422) {
      logTest('Error Handling - Empty Query', true, 'Properly rejected empty query');
    } else {
      logTest('Error Handling - Empty Query', false, 'Should have rejected empty query');
    }
  } catch (error) {
    logTest('Error Handling - Empty Query', false, error.message);
  }
}

async function testMultipleDocuments() {
  console.log('\n📚 Testing Multiple Document Upload...');

  // Upload second document
  const testContent2 = `
    Quebec Highway Safety Code
    Offence No: 987654321

    Section 448: Speeding
    Every driver who exceeds the speed limit is liable to a fine.

    Penalties:
    - 1-20 km/h over: $100-$200 + 2 points
    - 21-30 km/h over: $200-$300 + 4 points
    - 31+ km/h over: $400-$600 + 6 points
  `;

  const blob2 = new Blob([testContent2], { type: 'application/pdf' });
  const formData2 = new FormData();
  formData2.append('file', blob2, 'quebec_traffic_law.pdf');
  formData2.append('user_id', TEST_CONFIG.testUserId);

  try {
    const response = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/upload`, {
      method: 'POST',
      body: formData2,
      timeout: TEST_CONFIG.testTimeout
    });

    if (response.ok) {
      const data = await response.json();

      // Query about both provinces
      const comparisonQuery = {
        message: "Compare speeding penalties in Ontario and Quebec",
        top_k: 8
      };

      const chatResponse = await fetch(`${TEST_CONFIG.backendUrl}/api/artillery/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(comparisonQuery),
        timeout: TEST_CONFIG.testTimeout
      });

      if (chatResponse.ok) {
        const chatData = await chatResponse.json();
        const mentionsOntario = chatData.answer.toLowerCase().includes('ontario');
        const mentionsQuebec = chatData.answer.toLowerCase().includes('quebec');

        if (mentionsOntario && mentionsQuebec) {
          logTest('Multiple Documents', true, 'Query successfully retrieved information from both documents');
          return true;
        } else {
          logTest('Multiple Documents', false, 'Query did not retrieve information from both documents');
          return false;
        }
      } else {
        logTest('Multiple Documents', false, 'Chat query failed');
        return false;
      }
    } else {
      logTest('Multiple Documents', false, 'Second document upload failed');
      return false;
    }
  } catch (error) {
    logTest('Multiple Documents', false, error.message);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting PLAZA-AI Frontend Testing Suite\n');
  console.log('=' .repeat(50));
  console.log('PLAZA-AI ARTILLERY FRONTEND TESTS');
  console.log('=' .repeat(50));

  // Run all tests
  const backendOk = await testBackendConnection();
  const frontendOk = await testFrontendConnection();

  if (!backendOk) {
    console.log('\n❌ Backend is not running. Please start the backend server first:');
    console.log('cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000');
    return;
  }

  let uploadResult = null;
  if (backendOk) {
    uploadResult = await testDocumentUpload();
    await testChatQuery(uploadResult?.offenceNumber);
    await testOffenceNumberFiltering();
    await testErrorHandling();
    await testMultipleDocuments();
  }

  // Print results
  console.log('\n' + '=' .repeat(50));
  console.log('TEST RESULTS SUMMARY');
  console.log('=' .repeat(50));

  testResults.details.forEach((test, index) => {
    const status = test.status ? '✅ PASS' : '❌ FAIL';
    console.log(`${index + 1}. ${status} ${test.testName}`);
    if (test.message) {
      console.log(`   ${test.message}`);
    }
  });

  console.log('\n' + '=' .repeat(50));
  console.log(`FINAL SCORE: ${testResults.passed}/${testResults.total} tests passed`);

  const successRate = (testResults.passed / testResults.total) * 100;
  if (successRate >= 90) {
    console.log('🎉 EXCELLENT: Frontend is PRODUCTION READY!');
  } else if (successRate >= 75) {
    console.log('⚠️ GOOD: Frontend mostly working, minor issues to fix');
  } else {
    console.log('❌ NEEDS WORK: Significant issues to address');
  }

  console.log('=' .repeat(50));

  // Recommendations
  if (testResults.failed > 0) {
    console.log('\n🔧 RECOMMENDATIONS:');
    if (!backendOk) {
      console.log('- Start backend server: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000');
    }
    if (!frontendOk) {
      console.log('- Start frontend server: cd frontend && npm start');
    }
    console.log('- Check browser console for JavaScript errors');
    console.log('- Verify CORS is properly configured');
    console.log('- Check network tab for failed requests');
  }
}

// Run tests
runAllTests().catch(error => {
  console.error('Test suite failed:', error);
  process.exit(1);
});