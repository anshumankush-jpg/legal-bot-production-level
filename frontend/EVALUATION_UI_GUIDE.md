# Evaluation UI Guide

## ✅ What's Been Implemented

### 1. Design Tokens Integration
- ✅ Design tokens imported in `styles.scss`
- ✅ Global styles updated to use tokens
- ✅ Material components themed with navy/teal
- ✅ Chat component updated with design tokens
- ✅ Evaluation component uses design system

### 2. Evaluation System
- ✅ **Evaluation Service** (`evaluation.service.ts`)
  - Loads Ontario test cases
  - Runs tests against backend
  - Evaluates responses against expected outputs
  - Returns PASS/FAIL results

- ✅ **Evaluation Component** (`evaluation.component.ts`)
  - Displays all test cases
  - Shows expected vs actual outputs
  - PASS/FAIL indicators
  - Response time tracking
  - Expandable answer view

### 3. Navigation
- ✅ Evaluation route added (`/evaluation`)
- ✅ Dev-only navigation link (controlled by `environment.showEvaluation`)
- ✅ Hidden in production builds

### 4. OCR Edge Cases
- ✅ Upload component handles OCR warnings
- ✅ Partial parse detection
- ✅ Editable text area for corrections
- ✅ Retry OCR functionality

## 🎯 How to Use

### Running Evaluations

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Navigate to Evaluation:**
   - Go to `http://localhost:4200/evaluation`
   - Or click "Evaluation" in navigation (dev mode only)

4. **Run Tests:**
   - Click "Run All Tests" button
   - Watch as tests execute
   - Review PASS/FAIL results
   - Expand "View Model Answer" to see full responses

### Understanding Results

**PASS Criteria:**
- All required phrases present
- No forbidden phrases
- Offence correctly identified
- Demerit points correct
- Both FIGHT and PAY options mentioned
- Disclaimer present

**FAIL Reasons:**
- Missing required phrases
- Contains forbidden phrases
- Offence not identified
- Incorrect demerit points
- Missing options
- No disclaimer

## 📊 Test Cases Included

1. **Test 001:** Speeding ticket (45 km/h in 30 km/h zone)
   - Checks: Options, demerit points, fine amount

2. **Test 002:** Red light violation
   - Checks: Consequences, insurance impact

3. **Test 003:** Distracted driving
   - Checks: Fight process, deadlines

## 🔧 Customization

### Adding More Test Cases

Edit `evaluation.service.ts`:

```typescript
private testCases: EvaluationTestCase[] = [
  // Add your test case here
  {
    id: 'test_004',
    description: 'Your test description',
    jurisdiction: 'Ontario',
    ticket_data: { ... },
    question: 'Your question',
    expected_output: { ... }
  }
];
```

### Changing Evaluation Criteria

Modify `evaluateResponse()` method in `evaluation.service.ts` to add/remove checks.

### Styling

All styles use design tokens. Update `_design-tokens.scss` to change colors, spacing, etc.

## 🚀 Next Steps

1. **Backend Integration:**
   - Create `POST /api/evaluation/run` endpoint
   - Move evaluation logic to backend
   - Return structured results

2. **More Test Cases:**
   - Add California test cases
   - Add edge cases
   - Add multi-language tests

3. **Analytics:**
   - Track evaluation runs
   - Store results over time
   - Show trends

4. **Export Results:**
   - Download as CSV/JSON
   - Share results
   - Compare runs

---

**The evaluation UI is ready to use! Navigate to `/evaluation` and start testing.**

