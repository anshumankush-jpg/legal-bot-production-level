# 🚫 Frontend Disabled

## Status: DISABLED

The frontend has been temporarily disabled while a new frontend is being built.

### What Was Disabled:
- ✅ `package.json` → `package.json.disabled`
- ✅ `angular.json` → `angular.json.disabled`
- ✅ `src/` → `src.disabled/`

### To Re-enable:
1. Rename files back:
   ```bash
   cd frontend
   Rename-Item package.json.disabled package.json
   Rename-Item angular.json.disabled angular.json
   Rename-Item src.disabled src
   ```

2. Restart frontend:
   ```bash
   npm start
   ```

### Current Status:
- **Backend:** Running at http://localhost:8000
- **Frontend:** DISABLED
- **New Frontend:** To be built

---

**Note:** The frontend code is preserved in `.disabled` files/directories. You can restore it anytime.

