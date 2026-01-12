# Legal Document Generation Feature - Complete Guide

## Overview

This comprehensive legal document generation system allows users to create various types of legal documents including sue letters, contracts, amendments, NDAs, wills, and more. The system integrates with external APIs and provides AI-powered document generation with PDF export capabilities.

---

## Features

### 1. **Document Types Supported**

The system supports the following document types:

#### ⚖️ **Sue Letter (Legal Complaint)**
- File legal complaints against defendants
- Collects plaintiff and defendant information
- Includes legal grounds, damages, and relief sought
- Generates court-ready complaint format

#### 📝 **Amendment to Contract**
- Modify existing contract terms
- Specify sections to amend
- Document reasons for changes
- Include new terms and effective dates

#### 🤐 **Non-Disclosure Agreement (NDA)**
- Protect confidential information
- Define disclosing and receiving parties
- Set confidentiality terms and duration
- Include exceptions and remedies

#### 📜 **Last Will and Testament**
- Estate planning document
- Appoint executors and guardians
- Specify beneficiaries and bequests
- Include witness signatures

#### ✍️ **Power of Attorney**
- Authorize someone to act on your behalf
- Define specific powers granted
- Set effective dates
- Option for durable (survives incapacity)

#### 🏠 **Lease Agreement**
- Residential property rental
- Define landlord and tenant obligations
- Set rent, deposit, and term
- Include utilities and pet policies

#### 💼 **Employment Contract**
- Employment agreement
- Define position, salary, and benefits
- Set work hours and probation period
- Include termination notice requirements

#### 🤝 **Business Contract**
- General business agreements
- Define obligations for both parties
- Set payment terms and contract duration
- Include dispute resolution clauses

---

## User Interface

### Multi-Step Wizard

The document generator uses a 3-step wizard interface:

**Step 1: Select Document Type**
- Visual grid of document types with icons
- Clear descriptions for each type
- Click to select

**Step 2: Fill Details**
- Dynamic form based on document type
- Required and optional fields clearly marked
- Jurisdiction selector (US states, Canadian provinces)
- Real-time validation
- Helpful placeholders and descriptions

**Step 3: Preview & Download**
- Full document preview
- Edit button to go back and modify
- Copy to clipboard
- Download as TXT
- Download as PDF (formatted)

### Progress Indicator

Visual progress bar shows current step:
- ① Select Type
- ② Fill Details
- ③ Preview & Download

---

## Technical Architecture

### Frontend Components

#### **DocumentGenerator.jsx**
Main component that orchestrates the document generation flow.

**Key Features:**
- Multi-step wizard interface
- Dynamic form generation based on document type
- Form validation
- API integration for document generation
- PDF generation using jsPDF
- Copy to clipboard functionality

**Props:**
- `onClose`: Function to close the modal
- `lawCategory`: Current law category for context
- `userId`: User identifier for tracking

**State Management:**
```javascript
- step: Current wizard step (1-3)
- documentType: Selected document type
- jurisdiction: Selected jurisdiction
- formData: User-filled form data
- generatedDocument: Generated document content
- loading: Loading state
- error: Error messages
- previewMode: Preview/edit toggle
```

#### **DocumentGenerator.css**
Comprehensive styling with:
- Modern gradient header
- Responsive grid layout
- Smooth animations
- Mobile-friendly design
- Accessible form controls

### Backend Services

#### **document_generation_service.py**
Core service for generating legal documents.

**Key Methods:**
```python
async def generate_document(
    document_type: str,
    form_data: Dict[str, Any],
    jurisdiction: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]
```

**Document Templates:**
- `_generate_sue_letter()`: Legal complaint format
- `_generate_amendment()`: Contract amendment
- `_generate_nda()`: Non-disclosure agreement
- `_generate_will()`: Last will and testament
- `_generate_power_of_attorney()`: Power of attorney
- `_generate_lease_agreement()`: Lease agreement
- `_generate_employment_contract()`: Employment contract
- `_generate_business_contract()`: Business contract

**Template Features:**
- Professional legal formatting
- Jurisdiction-specific language
- Signature blocks
- Witness sections (where applicable)
- Legal disclaimers
- Date formatting

#### **API Endpoint**
```python
POST /api/legal/generate-document
```

**Request Body:**
```json
{
  "document_type": "sue_letter",
  "jurisdiction": "US-CA",
  "form_data": {
    "plaintiff_name": "John Doe",
    "defendant_name": "Jane Smith",
    "legal_grounds": "Breach of contract...",
    // ... other fields
  },
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_sue_letter_1234567890",
  "document_type": "sue_letter",
  "content": "LEGAL COMPLAINT\n\n...",
  "source": "AI-Powered Document Generator",
  "jurisdiction": "US-CA",
  "generated_at": "2026-01-09T12:00:00",
  "note": "This document has been generated automatically..."
}
```

---

## Security & Access Control

### Role-Based Access Control (RBAC)

Document generation requires **STANDARD** role or higher.

**Permission Levels:**
- **GUEST**: No access
- **STANDARD**: Full document generation access
- **PREMIUM**: Full access + priority support
- **ADMIN**: Full access + analytics

**Implementation:**
```python
# In rbac_service.py
Permission.API_DOCUMENT_GENERATION = "api:document_generation"

# Added to STANDARD role permissions
UserRole.STANDARD: {
    Permission.API_DOCUMENT_GENERATION,
    # ... other permissions
}
```

**Access Check in Endpoint:**
```python
access_check = rbac.can_use_api(user_role, "document_generation")
if not access_check["has_access"]:
    return {
        "success": False,
        "error": "Access denied",
        "upgrade_info": upgrade_info
    }
```

---

## PDF Generation

### Using jsPDF

The system uses **jsPDF** library for client-side PDF generation.

**Features:**
- Professional formatting
- Page breaks
- Headers and footers
- Page numbering
- Proper margins
- Text wrapping

**Implementation:**
```javascript
const handleDownloadPDF = () => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  
  // Title
  doc.setFontSize(16);
  doc.setFont(undefined, 'bold');
  doc.text(documentTypes[documentType].name, margin, margin);
  
  // Content with text wrapping
  doc.setFontSize(11);
  const lines = doc.splitTextToSize(content, maxWidth);
  
  // Handle page breaks
  lines.forEach(line => {
    if (y > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += 7;
  });
  
  // Footer with page numbers
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.text(`Page ${i} of ${totalPages}`, pageWidth / 2, pageHeight - 10);
  }
  
  doc.save(`${documentType}_${Date.now()}.pdf`);
};
```

---

## API Integration

### External Legal APIs

The system is designed to integrate with external legal APIs:

#### **LegalZoom API** (Amendment Generation)
```javascript
// Endpoint: POST /generate-amendment
// Purpose: Generate amendments to contracts
// Status: Mock implementation (configure API key to enable)
```

#### **LexisNexis API** (Case Lookup)
```javascript
// Endpoint: POST /case-lookup
// Purpose: Search legal cases and precedents
// Status: Mock implementation (configure API key to enable)
```

#### **CaseText API** (Case Search)
```javascript
// Endpoint: POST /cases/search
// Purpose: Advanced case search with filters
// Status: Mock implementation (configure API key to enable)
```

### Configuration

To enable real API integrations, set environment variables:

```bash
# In backend/.env
LEGALZOOM_API_KEY=your_legalzoom_key
LEXISNEXIS_API_KEY=your_lexisnexis_key
CASETEXT_API_KEY=your_casetext_key
WESTLAW_API_KEY=your_westlaw_key
```

**Mock Mode:**
When API keys are not configured, the system uses mock data for demonstration purposes. This allows testing without requiring paid API subscriptions.

---

## Integration with Chat History

### Searchable Document History

Generated documents are automatically integrated with the chat history system:

**Features:**
- All generated documents are saved
- Searchable by document type, content, or date
- Quick access from chat history modal
- Document regeneration from history

**Implementation:**
```javascript
// Save document to history
await fetch('http://localhost:8000/api/chat-history/save', {
  method: 'POST',
  body: JSON.stringify({
    user_id: userId,
    session_id: sessionId,
    message: `Generated ${documentType}`,
    response: generatedDocument.content,
    metadata: {
      document_type: documentType,
      document_id: generatedDocument.document_id,
      jurisdiction: jurisdiction
    }
  })
});
```

---

## Usage Examples

### Example 1: Generating a Sue Letter

1. Click **"📄 Documents"** button in chat interface
2. Select **"⚖️ Sue Letter (Legal Complaint)"**
3. Fill in the form:
   - Plaintiff Name: John Doe
   - Defendant Name: Jane Smith
   - Legal Grounds: Breach of contract - failed to deliver goods
   - Relief Sought: $50,000 in damages
   - Incident Date: 2025-12-01
4. Click **"Generate Document"**
5. Review the generated complaint
6. Click **"📄 Download PDF"** to save

### Example 2: Creating an NDA

1. Click **"📄 Documents"** button
2. Select **"🤐 Non-Disclosure Agreement (NDA)"**
3. Fill in the form:
   - Disclosing Party: Tech Corp Inc.
   - Receiving Party: Consultant LLC
   - Purpose: Software development project
   - Confidential Info: Source code, trade secrets, customer data
   - Term: 2 years
4. Generate and download

### Example 3: Amendment to Contract

1. Click **"📄 Documents"** button
2. Select **"📝 Amendment to Contract"**
3. Fill in the form:
   - Original Contract: Service Agreement 2024
   - Party A: Company A
   - Party B: Company B
   - Sections to Amend: Section 5 (Payment Terms)
   - Reason: Adjust payment schedule
   - New Terms: Monthly payments instead of quarterly
4. Generate and review

---

## Best Practices

### For Users

1. **Review Carefully**: Always review generated documents carefully before use
2. **Legal Review**: Have documents reviewed by a licensed attorney
3. **Customize**: Edit documents to fit your specific needs
4. **Save Copies**: Download both TXT and PDF versions
5. **Jurisdiction**: Select the correct jurisdiction for your case

### For Developers

1. **Validation**: Always validate user input before generation
2. **Error Handling**: Provide clear error messages
3. **Security**: Sanitize all user inputs
4. **Logging**: Log all document generation requests
5. **Backup**: Store generated documents securely

---

## Troubleshooting

### Common Issues

**Issue: Document not generating**
- Check backend server is running
- Verify API endpoint is accessible
- Check browser console for errors
- Ensure all required fields are filled

**Issue: PDF download fails**
- Check jsPDF library is loaded
- Try downloading as TXT instead
- Check browser console for errors
- Verify browser allows downloads

**Issue: Access denied error**
- Check user role permissions
- Verify authentication token
- Contact admin to upgrade role

**Issue: Mock data instead of real API**
- Configure API keys in environment variables
- Restart backend server
- Check API key validity

---

## Future Enhancements

### Planned Features

1. **Google Docs Integration**
   - Export directly to Google Docs
   - Collaborative editing
   - Cloud storage

2. **Advanced Templates**
   - More document types
   - Industry-specific templates
   - Customizable templates

3. **AI Enhancement**
   - AI-powered clause suggestions
   - Legal language optimization
   - Risk assessment

4. **E-Signature Integration**
   - DocuSign integration
   - Adobe Sign integration
   - Built-in e-signature

5. **Document Management**
   - Document versioning
   - Folder organization
   - Sharing capabilities

6. **Multi-language Support**
   - Generate documents in multiple languages
   - Legal terminology translation
   - Jurisdiction-specific language

---

## Legal Disclaimer

**IMPORTANT NOTICE:**

This is an automated document generation system. The documents generated are templates and should NOT be used without review by a qualified legal professional.

- **Not Legal Advice**: This system does not provide legal advice
- **Attorney Review Required**: All documents should be reviewed by a licensed attorney
- **Jurisdiction Specific**: Legal requirements vary by jurisdiction
- **No Guarantee**: No guarantee of legal validity or completeness
- **User Responsibility**: Users are responsible for ensuring documents meet their needs

Always consult with a qualified attorney before using any legal document.

---

## Support

For issues or questions:
- Check this documentation
- Review error messages carefully
- Check browser console for technical errors
- Contact system administrator
- Consult with legal professional for legal questions

---

## Version History

**Version 1.0.0** (January 9, 2026)
- Initial release
- 8 document types supported
- PDF generation
- RBAC integration
- Mock API support
- Chat history integration

---

## Credits

**Developed by:** PLAZA-AI Legal Team
**Technology Stack:**
- Frontend: React, jsPDF
- Backend: Python, FastAPI
- APIs: LegalZoom, LexisNexis, CaseText (planned)

---

## License

Copyright © 2026 PLAZA-AI. All rights reserved.

This system is for authorized use only. Unauthorized access or use is prohibited.

---

**End of Documentation**
