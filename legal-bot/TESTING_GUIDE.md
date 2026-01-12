# Testing Guide - Enhanced Legal Assistant UI

## Overview

This guide provides comprehensive testing procedures for all new features in the Enhanced Legal Assistant UI.

## Pre-Testing Setup

### 1. Start the Backend

```bash
cd legal-bot/backend
python -m uvicorn app.main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "backend_running": true,
  "openai_configured": true,
  "version": "1.0.0"
}
```

### 2. Start the Frontend

```bash
cd legal-bot/frontend
npm run dev
```

Access the app at: `http://localhost:5173`

## Test Cases

### Test 1: Navigation Bar

**Objective**: Verify all navigation buttons work correctly

**Steps**:
1. Open the application
2. Click each navigation button:
   - New Chat
   - Search Chats
   - Images
   - Apps
   - Codex
   - Projects

**Expected Results**:
- ✅ Each button changes the active state (highlighted)
- ✅ Main content area updates to show corresponding view
- ✅ Icons and labels are visible
- ✅ Hover effects work smoothly

**Pass Criteria**: All buttons respond correctly with visual feedback

---

### Test 2: Chat Sidebar

**Objective**: Test sidebar functionality and chat management

**Steps**:
1. Click "New Chat" button in sidebar
2. Send a message in the chat
3. Start another new chat
4. Search for chats using the search box
5. Click on a saved chat to load it
6. Hover over a chat and click delete
7. Click the collapse toggle

**Expected Results**:
- ✅ New chat creates a new conversation
- ✅ Chats are saved automatically
- ✅ Search filters chats in real-time
- ✅ Clicking a chat loads its messages
- ✅ Delete button appears on hover
- ✅ Sidebar collapses/expands smoothly

**Pass Criteria**: All sidebar features work without errors

---

### Test 3: Chat History Search

**Objective**: Test advanced search functionality

**Steps**:
1. Click "Search Chats" in navigation or sidebar
2. Enter a search query
3. Press Enter or click Search button
4. View search results
5. Click on a result
6. Switch between "Sessions" and "Search Results" tabs
7. Delete a session

**Expected Results**:
- ✅ Search modal opens
- ✅ Search returns relevant results
- ✅ Search terms are highlighted in results
- ✅ Clicking a result loads that conversation
- ✅ Tabs switch correctly
- ✅ Session deletion works with confirmation

**Pass Criteria**: Search finds relevant chats and displays them correctly

---

### Test 4: Case Lookup API

**Objective**: Test case search functionality

**Steps**:
1. Start a chat
2. Click "🔍 Case Lookup" button
3. Enter search query: "Miranda"
4. Select jurisdiction: "US"
5. Set year range: 1960-2024
6. Click "Search Cases"
7. Click on a case result
8. Click "View Full Case" link

**Expected Results**:
- ✅ Modal opens with search form
- ✅ Search returns case results (mock or real)
- ✅ Results show case name, citation, court, year
- ✅ Relevance score is displayed
- ✅ Clicking a case inserts it into chat
- ✅ External links open in new tab

**API Endpoint Test**:
```bash
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Miranda v. Arizona",
    "jurisdiction": "US",
    "year_from": 1960,
    "year_to": 2024,
    "limit": 10
  }'
```

**Pass Criteria**: Case search returns results and displays them properly

---

### Test 5: Amendment Generator API

**Objective**: Test document amendment generation

**Steps**:
1. Click "📝 Amendments" button
2. Select document type: "Contract"
3. Select jurisdiction: "US-NY"
4. Enter amendment text: "Change payment terms from 30 to 45 days"
5. Fill in Party A: "Company A"
6. Fill in Party B: "Company B"
7. Set effective date
8. Click "Generate Amendment"
9. Click "Copy" button
10. Click "Download" button

**Expected Results**:
- ✅ Modal opens with form
- ✅ Document types are available
- ✅ Amendment generates successfully
- ✅ Generated text is properly formatted
- ✅ Copy button copies to clipboard
- ✅ Download creates a text file

**API Endpoint Test**:
```bash
curl -X POST http://localhost:8000/api/legal/generate-amendment \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "contract",
    "case_details": {
      "amendment_text": "Change payment terms",
      "party_a": "Company A",
      "party_b": "Company B",
      "effective_date": "2024-02-01"
    },
    "jurisdiction": "US-NY"
  }'
```

**Pass Criteria**: Amendment is generated and can be copied/downloaded

---

### Test 6: Role-Based Access Control

**Objective**: Test RBAC functionality

**Steps**:
1. Test as Guest user (no token)
2. Try to access "Case Lookup"
3. Try to access "Codex"
4. Try to access "Projects"
5. Generate a Standard token:
```bash
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=standard"
```
6. Try Case Lookup again
7. Generate a Premium token:
```bash
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"
```
8. Try all features

**Expected Results**:
- ✅ Guest: Access denied banner appears
- ✅ Standard: Limited features available
- ✅ Premium: Most features available
- ✅ Banner shows upgrade information
- ✅ Current role is displayed
- ✅ Required role is shown

**Pass Criteria**: Access control works correctly for each role

---

### Test 7: Translation API

**Objective**: Test multilingual support

**Steps**:
1. Send a message in chat
2. Test translation endpoint:
```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What are the penalties for speeding?",
    "target_language": "es",
    "source_language": "en"
  }'
```
3. Change language in preferences
4. Send another message
5. Verify response is in selected language

**Expected Results**:
- ✅ Translation endpoint returns translated text
- ✅ Language preference is saved
- ✅ Responses are in selected language
- ✅ Supported languages list is available

**Pass Criteria**: Translation works for all supported languages

---

### Test 8: Chat History Persistence

**Objective**: Test data persistence across sessions

**Steps**:
1. Start a new chat
2. Send several messages
3. Close the browser tab
4. Reopen the application
5. Check if chats are still there
6. Load a previous chat

**Expected Results**:
- ✅ Chats persist in localStorage
- ✅ All messages are preserved
- ✅ Timestamps are correct
- ✅ Chat metadata is intact

**Pass Criteria**: All data persists correctly

---

### Test 9: Responsive Design

**Objective**: Test UI on different screen sizes

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on:
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)
4. Test all features on each size

**Expected Results**:
- ✅ Navigation adapts to screen size
- ✅ Sidebar becomes collapsible on mobile
- ✅ Modals are responsive
- ✅ Text is readable on all sizes
- ✅ Buttons are touchable on mobile

**Pass Criteria**: UI works well on all screen sizes

---

### Test 10: Performance & Load Testing

**Objective**: Test performance with many chats

**Steps**:
1. Create 50+ chat sessions
2. Search through chats
3. Load different chats
4. Monitor browser console for errors
5. Check memory usage in DevTools

**Expected Results**:
- ✅ Search remains fast (<500ms)
- ✅ Chat loading is instant
- ✅ No memory leaks
- ✅ Smooth scrolling
- ✅ No console errors

**Pass Criteria**: App remains responsive with large data

---

## Integration Tests

### Test 11: End-to-End User Flow

**Scenario**: User researches a legal case and generates an amendment

**Steps**:
1. Open application
2. Select law type: "Business Law"
3. Start new chat
4. Ask: "What are the requirements for a valid contract?"
5. Click "Case Lookup"
6. Search for contract cases
7. Select a relevant case
8. Ask follow-up questions
9. Click "Amendments"
10. Generate a contract amendment
11. Download the amendment
12. Save the chat
13. Search for the chat later
14. Load and continue the conversation

**Expected Results**:
- ✅ Entire flow completes without errors
- ✅ All features work together seamlessly
- ✅ Data is preserved throughout
- ✅ User can pick up where they left off

**Pass Criteria**: Complete user journey works smoothly

---

## API Integration Tests

### Test 12: Backend API Health

```bash
# Test all endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api/artillery/health
```

### Test 13: Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/artillery/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the penalties for speeding in Ontario?",
    "law_category": "Traffic Law",
    "jurisdiction": "CA-ON",
    "top_k": 5
  }'
```

### Test 14: Upload Endpoint

```bash
curl -X POST http://localhost:8000/api/artillery/upload \
  -F "file=@test_document.pdf" \
  -F "user_id=test_user"
```

---

## Error Handling Tests

### Test 15: Network Errors

**Steps**:
1. Stop the backend server
2. Try to send a chat message
3. Try to search cases
4. Try to generate amendment

**Expected Results**:
- ✅ User-friendly error messages
- ✅ No application crashes
- ✅ Retry options available
- ✅ Offline indicator shown

### Test 16: Invalid Input

**Steps**:
1. Submit empty search query
2. Generate amendment without required fields
3. Enter invalid date formats
4. Upload unsupported file types

**Expected Results**:
- ✅ Validation messages appear
- ✅ Form doesn't submit
- ✅ Clear error descriptions
- ✅ Suggestions for correction

---

## Security Tests

### Test 17: XSS Prevention

**Steps**:
1. Try to inject script in chat: `<script>alert('xss')</script>`
2. Try to inject HTML: `<img src=x onerror=alert('xss')>`

**Expected Results**:
- ✅ Scripts are not executed
- ✅ HTML is escaped
- ✅ Content is sanitized

### Test 18: API Authentication

**Steps**:
1. Call protected endpoints without token
2. Call with invalid token
3. Call with expired token

**Expected Results**:
- ✅ 401 Unauthorized for missing token
- ✅ 401 for invalid token
- ✅ 401 for expired token

---

## Test Results Template

```markdown
## Test Run: [Date]

### Environment
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Browser: Chrome 120.0
- OS: Windows 11

### Results Summary
- Total Tests: 18
- Passed: ✅ 18
- Failed: ❌ 0
- Skipped: ⏭️ 0

### Detailed Results
| Test | Status | Notes |
|------|--------|-------|
| Navigation Bar | ✅ Pass | All buttons work |
| Chat Sidebar | ✅ Pass | Search works well |
| Case Lookup | ✅ Pass | Mock data displayed |
| ... | ... | ... |

### Issues Found
1. None

### Performance Metrics
- Chat load time: 45ms
- Search response: 120ms
- API response: 350ms

### Recommendations
- All tests passed successfully
- Ready for deployment
```

---

## Automated Testing

### Setup Jest Tests

```bash
cd legal-bot/frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Example Test File

```javascript
// NavigationBar.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import NavigationBar from './NavigationBar';

test('renders navigation buttons', () => {
  render(<NavigationBar />);
  expect(screen.getByText('New Chat')).toBeInTheDocument();
  expect(screen.getByText('Search Chats')).toBeInTheDocument();
});

test('clicking new chat calls handler', () => {
  const handleNewChat = jest.fn();
  render(<NavigationBar onNewChat={handleNewChat} />);
  fireEvent.click(screen.getByText('New Chat'));
  expect(handleNewChat).toHaveBeenCalled();
});
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Enhanced UI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
        working-directory: ./legal-bot/frontend
      - name: Run tests
        run: npm test
        working-directory: ./legal-bot/frontend
```

---

## Conclusion

Follow this testing guide to ensure all features work correctly before deployment. Update test results regularly and maintain this document as new features are added.

**Last Updated**: January 2026
