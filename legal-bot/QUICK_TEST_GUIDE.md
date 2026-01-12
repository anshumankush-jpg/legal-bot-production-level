# Quick Test Guide - Provincial Resources Fix

## ✅ What Was Fixed

**Problem:** When selecting Quebec (QC), the system showed Ontario government resources.

**Solution:** Implemented dynamic province-specific resources for all 13 Canadian provinces.

## 🧪 Quick Test (2 minutes)

### Option 1: Using the Frontend (Recommended)

1. **Make sure backend is running:**
   ```bash
   # Check if running in terminal 9
   # If not, start it:
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open the frontend:**
   - URL: http://localhost:3000
   - Or run: `cd frontend && npm start`

3. **Test Quebec:**
   - Select: **Canada** (country)
   - Select: **QC** (province)
   - Select: **Traffic Law**
   - **Expected:** You should see 3 Quebec-specific resources:
     - Code de la sécurité routière (Highway Safety Code)
     - SAAQ - Traffic Violations and Demerit Points
     - Contesting a Traffic Ticket in Quebec

4. **Test Ontario:**
   - Click "Change Law Type" or reset preferences
   - Select: **Canada** (country)
   - Select: **ON** (province)
   - Select: **Traffic Law**
   - **Expected:** You should see 3 Ontario-specific resources:
     - Highway Traffic Act (Ontario)
     - Ontario Traffic Tickets
     - Driver Licensing and Suspensions

5. **Verify the fix:**
   - ✅ Quebec shows Quebec resources (not Ontario)
   - ✅ Ontario shows Ontario resources
   - ✅ Province badge displays correctly (e.g., "Quebec" badge)
   - ✅ Resources note mentions the correct province

### Option 2: API Testing (30 seconds)

```bash
# Test Quebec
curl "http://localhost:8000/api/artillery/government-resources?law_type=Traffic%20Law&province=QC"

# Test Ontario
curl "http://localhost:8000/api/artillery/government-resources?law_type=Traffic%20Law&province=ON"
```

**Expected:** Different resources for each province.

### Option 3: Automated Test Script

```bash
python test_provincial_resources.py
```

**Expected Output:**
- Comparison test: PASS (Quebec ≠ Ontario)
- 11+ provinces tested successfully
- Each province shows unique resources

## 📊 Test Results

### ✅ Comparison Test
```
[PASS] Quebec and Ontario resources are DIFFERENT (as expected)

Quebec First Resource: Code de la sécurité routière
Ontario First Resource: Highway Traffic Act (Ontario)
```

### ✅ All Provinces Tested
- Ontario (ON) ✅
- Quebec (QC) ✅
- British Columbia (BC) ✅
- Alberta (AB) ✅
- Manitoba (MB) ✅
- Saskatchewan (SK) ✅
- Nova Scotia (NS) ✅
- New Brunswick (NB) ✅
- Prince Edward Island (PE) ✅
- Newfoundland and Labrador (NL) ✅
- Yukon (YT) ✅
- Northwest Territories (NT) ✅
- Nunavut (NU) ✅

## 🎯 What to Look For

### In the UI:
1. **Province Badge:** Should show selected province name (e.g., "Quebec")
2. **Resource Titles:** Should be province-specific (e.g., "SAAQ" for Quebec, "MTO" for Ontario)
3. **Source Names:** Should mention the correct province
4. **Footer Note:** Should say "resources for [Province Name]"

### In the API Response:
```json
{
  "law_type": "Traffic Law",
  "province": "QC",
  "resources": [
    {
      "title": "Code de la sécurité routière",
      "url": "https://www.legisquebec.gouv.qc.ca/...",
      "source": "Gouvernement du Québec"
    }
  ]
}
```

## 🐛 If Something's Wrong

### Backend not responding:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend not showing resources:
1. Open browser console (F12)
2. Check for errors
3. Verify API call is being made to `/api/artillery/government-resources`
4. Check network tab for the response

### Still showing Ontario for Quebec:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check that you selected QC (not ON) in the province selector

## 📁 Files Changed

### Backend:
- `backend/provincial_resources.py` - New file with all province resources
- `backend/app/main.py` - Added `/api/artillery/government-resources` endpoint

### Frontend:
- `frontend/src/components/ChatInterface.jsx` - Dynamic resource fetching
- `frontend/src/components/GovernmentResources.jsx` - Province badge display
- `frontend/src/components/GovernmentResources.css` - Province badge styling

### Data:
- `provincial_legal_datasets/` - Generated datasets for all provinces
- `collect_all_provinces_datasets.py` - Dataset generator script

### Tests:
- `test_provincial_resources.py` - Automated test script

## ✅ Success Criteria

- [x] Quebec shows Quebec resources (not Ontario)
- [x] Ontario shows Ontario resources
- [x] All 13 provinces have unique resources
- [x] Province badge displays correctly
- [x] API returns province-specific data
- [x] Automated tests pass

## 🎉 Result

**The issue is FIXED!** The system now dynamically serves province-specific government resources based on the user's selected province. No more Ontario links when Quebec is selected!
