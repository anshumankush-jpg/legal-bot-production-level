# Legal Document Generation - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you quickly set up and use the legal document generation feature.

---

## Prerequisites

- Node.js and npm installed
- Python 3.8+ installed
- Backend server running
- Frontend application running

---

## Installation

### 1. Install Frontend Dependencies

```bash
cd legal-bot/frontend
npm install jspdf
```

### 2. Backend is Already Configured

The backend service is already included in the project. No additional installation needed!

---

## Usage

### Step 1: Access the Document Generator

1. Open the legal bot application
2. Complete onboarding and select your law type
3. In the chat interface, click the **"📄 Documents"** button in the top toolbar

### Step 2: Select Document Type

Choose from 8 document types:
- ⚖️ Sue Letter (Legal Complaint)
- 📝 Amendment to Contract
- 🤐 Non-Disclosure Agreement (NDA)
- 📜 Last Will and Testament
- ✍️ Power of Attorney
- 🏠 Lease Agreement
- 💼 Employment Contract
- 🤝 Business Contract

### Step 3: Fill in the Form

- Fill in all required fields (marked with *)
- Optional: Select jurisdiction (US states or Canadian provinces)
- Add any additional information in optional fields

### Step 4: Generate & Download

1. Click **"Generate Document"**
2. Review the generated document
3. Choose download option:
   - **📋 Copy**: Copy to clipboard
   - **💾 Download TXT**: Save as text file
   - **📄 Download PDF**: Save as formatted PDF

---

## Quick Examples

### Example 1: Generate an NDA (2 minutes)

```
1. Click "📄 Documents"
2. Select "🤐 Non-Disclosure Agreement"
3. Fill in:
   - Disclosing Party: Your Company
   - Receiving Party: Contractor Name
   - Purpose: Software development project
   - Confidential Info: Source code, trade secrets
   - Term: 2 years
4. Click "Generate Document"
5. Download PDF
```

### Example 2: Create a Sue Letter (3 minutes)

```
1. Click "📄 Documents"
2. Select "⚖️ Sue Letter"
3. Fill in:
   - Your Name: John Doe
   - Defendant Name: Jane Smith
   - Legal Grounds: Breach of contract
   - Relief Sought: $50,000 in damages
   - Incident Date: Select date
4. Click "Generate Document"
5. Download PDF
```

### Example 3: Employment Contract (3 minutes)

```
1. Click "📄 Documents"
2. Select "💼 Employment Contract"
3. Fill in:
   - Employer: Company Name
   - Employee: Employee Name
   - Position: Software Engineer
   - Salary: 80000
   - Start Date: Select date
4. Click "Generate Document"
5. Download PDF
```

---

## Features at a Glance

### ✅ What You Can Do

- Generate 8 types of legal documents
- Customize for different jurisdictions
- Preview before downloading
- Edit and regenerate
- Download as PDF or TXT
- Copy to clipboard
- Professional formatting
- Legal disclaimers included

### ⚠️ Important Notes

- **Not Legal Advice**: Documents are templates only
- **Attorney Review Required**: Always have documents reviewed by a lawyer
- **Jurisdiction Specific**: Select the correct jurisdiction
- **Customize**: Edit documents to fit your specific needs

---

## Troubleshooting

### Issue: "Access Denied" Error

**Solution:** Your user role may not have permission. Contact admin to upgrade to STANDARD role or higher.

### Issue: PDF Download Not Working

**Solution:** 
1. Try downloading as TXT instead
2. Check if browser blocks downloads
3. Try a different browser

### Issue: Document Not Generating

**Solution:**
1. Ensure all required fields are filled
2. Check backend server is running (http://localhost:8000)
3. Check browser console for errors

### Issue: Form Validation Errors

**Solution:**
- Fill in all fields marked with *
- Check date formats
- Ensure numeric fields contain only numbers

---

## API Configuration (Optional)

To enable real legal API integrations:

### 1. Get API Keys

Sign up for:
- LegalZoom API: https://www.legalzoom.com/developers
- LexisNexis API: https://www.lexisnexis.com/api
- CaseText API: https://casetext.com/api

### 2. Configure Environment Variables

Create/edit `backend/.env`:

```bash
# Legal API Keys
LEGALZOOM_API_KEY=your_legalzoom_key_here
LEXISNEXIS_API_KEY=your_lexisnexis_key_here
CASETEXT_API_KEY=your_casetext_key_here
```

### 3. Restart Backend

```bash
cd legal-bot/backend
# Stop the server (Ctrl+C)
# Start again
python -m uvicorn app.main:app --reload
```

**Note:** Without API keys, the system uses mock data for demonstration.

---

## Tips & Best Practices

### 📝 Document Creation Tips

1. **Be Specific**: Provide detailed information in all fields
2. **Review Carefully**: Always review generated documents
3. **Save Multiple Versions**: Download both TXT and PDF
4. **Keep Records**: Save all generated documents
5. **Legal Review**: Have a lawyer review before use

### 🔒 Security Tips

1. **Sensitive Information**: Be careful with personal data
2. **Secure Storage**: Store documents securely
3. **Access Control**: Only authorized users should access
4. **Backup**: Keep backups of important documents

### ⚡ Efficiency Tips

1. **Prepare Information**: Gather all information before starting
2. **Use Templates**: Save common information for reuse
3. **Batch Generation**: Generate multiple documents in one session
4. **Quick Edit**: Use the edit button to make small changes

---

## Keyboard Shortcuts

- **Esc**: Close document generator
- **Ctrl+C** (in preview): Copy document to clipboard
- **Ctrl+S** (in preview): Download as TXT

---

## Support

### Need Help?

1. Check the full documentation: `LEGAL_DOCUMENT_GENERATION_GUIDE.md`
2. Review error messages carefully
3. Check browser console (F12) for technical errors
4. Contact system administrator

### Legal Questions?

Always consult with a qualified attorney for:
- Legal advice
- Document validity
- Jurisdiction-specific requirements
- Complex legal matters

---

## Next Steps

After generating your document:

1. ✅ Review the document carefully
2. ✅ Consult with a licensed attorney
3. ✅ Customize for your specific needs
4. ✅ Get signatures (if required)
5. ✅ File with appropriate court/agency (if applicable)
6. ✅ Keep copies for your records

---

## Feature Roadmap

### Coming Soon

- 🔄 Google Docs integration
- 📧 Email documents directly
- 🔐 E-signature integration
- 📁 Document management system
- 🌐 Multi-language support
- 🤖 AI-powered clause suggestions

---

## Quick Reference Card

### Document Types & Use Cases

| Document | Use Case | Time |
|----------|----------|------|
| Sue Letter | File lawsuit | 3 min |
| Amendment | Modify contract | 2 min |
| NDA | Protect secrets | 2 min |
| Will | Estate planning | 4 min |
| Power of Attorney | Authorize agent | 3 min |
| Lease | Rent property | 3 min |
| Employment | Hire employee | 3 min |
| Business Contract | Business deal | 3 min |

### Required Fields by Document

**Sue Letter:**
- Plaintiff name ✓
- Defendant name ✓
- Legal grounds ✓
- Relief sought ✓

**NDA:**
- Disclosing party ✓
- Receiving party ✓
- Purpose ✓
- Confidential info ✓
- Term (years) ✓

**Employment Contract:**
- Employer name ✓
- Employee name ✓
- Position ✓
- Salary ✓
- Start date ✓

---

## Legal Disclaimer

⚠️ **IMPORTANT:**

This system generates document templates only. It does NOT:
- Provide legal advice
- Replace an attorney
- Guarantee legal validity
- Ensure compliance with local laws

**Always consult a licensed attorney before using any legal document.**

---

## Version

**Version:** 1.0.0  
**Last Updated:** January 9, 2026  
**Status:** Production Ready

---

## Contact

For technical support or questions:
- Email: support@plaza-ai.com
- Documentation: See `LEGAL_DOCUMENT_GENERATION_GUIDE.md`

For legal questions:
- Consult a licensed attorney in your jurisdiction

---

**Happy Document Generating! 📄✨**
