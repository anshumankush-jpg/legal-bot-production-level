# Install Required Dependencies for Document Generation

## Quick Install

Run this command in the `frontend` directory:

```bash
npm install jspdf
```

## What This Installs

- **jsPDF** (v2.5.1+): Client-side PDF generation library
  - Used for: Converting generated documents to PDF format
  - License: MIT
  - Size: ~500KB
  - Documentation: https://github.com/parallax/jsPDF

## Verify Installation

After installation, verify:

```bash
# Check package.json
cat package.json | grep jspdf

# Expected output:
# "jspdf": "^2.5.1"
```

## Alternative: Manual Installation

If npm install doesn't work, try:

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules
rm package-lock.json

# Reinstall all dependencies
npm install

# Install jsPDF
npm install jspdf
```

## Usage in Code

After installation, jsPDF is imported in `DocumentGenerator.jsx`:

```javascript
import jsPDF from 'jspdf';

// Usage
const doc = new jsPDF();
doc.text('Hello world!', 10, 10);
doc.save('document.pdf');
```

## Troubleshooting

### Issue: "Cannot find module 'jspdf'"

**Solution:**
```bash
npm install jspdf --save
```

### Issue: Build errors after installation

**Solution:**
```bash
# Restart development server
npm start
```

### Issue: TypeScript errors

**Solution:**
```bash
# Install type definitions
npm install --save-dev @types/jspdf
```

## Complete Dependencies List

After installation, your `package.json` should include:

```json
{
  "dependencies": {
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "jspdf": "^2.5.1",
    // ... other dependencies
  }
}
```

## Done!

jsPDF is now installed and ready to use for PDF generation.

See `DOCUMENT_GENERATION_QUICK_START.md` for usage instructions.
