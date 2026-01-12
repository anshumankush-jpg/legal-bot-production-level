# Quick Start Guide - Advanced Legal Testing

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements_testing.txt
```

### Step 2: Make Sure Backend is Running

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Run the Test Suite

```bash
python advanced_legal_source_test.py
```

**Expected Output:**
```
================================================================================
ADVANCED LEGAL SOURCE TEST SUITE
================================================================================
Start Time: 2026-01-08 12:00:00
Backend URL: http://localhost:8000
Total Tests: 25
================================================================================

[*] Checking backend health...
[OK] Backend is running!

################################################################################
Running Test 1/25
################################################################################

================================================================================
TEST #1: Criminal Law - Canada (Federal)
================================================================================
Question: What is the penalty for theft under $5000 in Canada?

--- RESPONSE STATUS ---
Answer: [OK] Under the Canadian Criminal Code, theft under $5000...
Citations: [OK] 5 sources

--- SOURCE VERIFICATION ---
Overall Score: 75.0%
...
```

### Step 4: Review Results

Results are saved to:
- **Console**: Real-time output
- **JSON File**: `advanced_legal_test_results_YYYYMMDD_HHMMSS.json`

### Step 5: Setup Daily Scraper (Optional)

```bash
# Run once to test
python legal_news_scraper.py

# Run with daily scheduler
python daily_legal_updater.py
```

---

## 📊 Understanding Your Results

### Test Summary Example

```
TEST SUMMARY
Total Tests: 25
[OK] Passed: 22 (88.0%)
[X] Failed: 3 (12.0%)

--- RESULTS BY LAW TYPE AND COUNTRY ---
Canada - Criminal Law: 5/5 (100.0%) ✓
Canada - Traffic Law: 5/5 (100.0%) ✓
USA - Criminal Law: 4/5 (80.0%)
USA - Traffic Law: 3/3 (100.0%) ✓
```

### What Each Score Means

| Score | Meaning | Action Needed |
|-------|---------|---------------|
| 90-100% | Excellent | None |
| 70-89% | Good | Minor improvements |
| 50-69% | Acceptable | Add more documents |
| 40-49% | Marginal | Needs attention |
| <40% | Failed | Missing critical sources |

---

## 🔧 Quick Fixes

### If Tests Are Failing

1. **Check Backend**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Vector Database**
   ```bash
   ls -lh backend/data/faiss_index.bin
   ```

3. **Re-run Ingestion**
   ```bash
   python process_and_ingest_all_laws.py
   ```

### If Scraper Isn't Working

1. **Test Internet Connection**
   ```bash
   curl https://www.justice.gc.ca
   ```

2. **Check Scraper Output**
   ```bash
   python legal_news_scraper.py
   cat legal_updates/legal_updates_$(date +%Y%m%d).json
   ```

3. **Reset Hash Database** (if needed)
   ```bash
   rm legal_updates/previous_updates.json
   python legal_news_scraper.py
   ```

---

## 📁 Files You'll Get

### After Running Tests

```
advanced_legal_test_results_20260108_120000.json  ← Full test results
```

### After Running Scraper

```
legal_updates/
├── legal_updates_20260108.json     ← Today's scraped updates
├── to_ingest_20260108.json         ← Ready for ingestion
└── previous_updates.json            ← Duplicate tracker
```

---

## 🎯 What to Test First

### Recommended Testing Order

1. **Criminal Law** (Most critical)
   - Tests #1-5 (Canada)
   - Tests #11-15 (USA)

2. **Traffic Law** (High volume)
   - Tests #6-10 (Canada)
   - Tests #16-18 (USA)

3. **Other Law Types**
   - Tests #19-25 (Family, Copyright, Employment, Constitutional)

### Running Specific Tests

Edit `advanced_legal_source_test.py`:

```python
# Only run Criminal Law tests
COMPREHENSIVE_TEST_CASES = [t for t in COMPREHENSIVE_TEST_CASES if 'Criminal Law' in t['law_type']]
```

---

## 💡 Pro Tips

### 1. Run Tests After Adding Documents

```bash
# Add new documents
python process_and_ingest_all_laws.py

# Wait 10 seconds for indexing
sleep 10

# Run tests
python advanced_legal_source_test.py
```

### 2. Compare Results Over Time

```bash
# Save results with descriptive names
python advanced_legal_source_test.py
mv advanced_legal_test_results_*.json results_before_update.json

# Make improvements...

python advanced_legal_source_test.py
mv advanced_legal_test_results_*.json results_after_update.json

# Compare
diff results_before_update.json results_after_update.json
```

### 3. Monitor Daily Updates

```bash
# Check how many updates today
cat legal_updates/legal_updates_$(date +%Y%m%d).json | grep "total_updates"

# List all updates
ls -lh legal_updates/legal_updates_*.json
```

---

## 🆘 Common Issues

### Issue: "Backend is not running"

**Solution:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: "No citations found"

**Solution:**
```bash
# Check if vector database exists
ls backend/data/faiss_index.bin

# If missing, run ingestion
python process_and_ingest_all_laws.py
```

### Issue: "All tests failing"

**Solution:**
```bash
# Check backend logs
tail -100 backend_detailed.log

# Restart backend
# Kill existing process
pkill -f "uvicorn app.main:app"

# Start fresh
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: "Scraper finds 0 updates"

**Solution:**
```bash
# Reset hash database
rm legal_updates/previous_updates.json

# Run again
python legal_news_scraper.py
```

---

## 📞 Next Steps

1. ✅ Run initial test suite
2. ✅ Review results
3. ✅ Add missing documents for low-scoring areas
4. ✅ Setup daily scraper
5. ✅ Schedule weekly ingestion of new updates

---

## 📖 Full Documentation

For complete details, see: **ADVANCED_TESTING_README.md**

---

**Quick Start Complete!** 🎉

You now have:
- ✅ 25 comprehensive test cases
- ✅ Automated daily legal news scraper
- ✅ Source verification system
- ✅ Daily update tracking

**Happy Testing!** 🚀
