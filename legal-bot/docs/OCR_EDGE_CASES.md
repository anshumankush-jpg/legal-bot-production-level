# OCR Edge Cases & Handling

## Common OCR Issues

### 1. Low Light Photos
**Problem:** Dark or poorly lit ticket images result in poor OCR accuracy.

**Solutions:**
- Pre-process image: Increase brightness/contrast
- Use adaptive thresholding
- Try multiple OCR engines (Tesseract, Google Vision, Azure Vision)

**UX Handling:**
```typescript
if (ocrConfidence < 0.7) {
  showMessage("The image quality is low. Please try taking another photo with better lighting.");
  offerManualEntry();
}
```

### 2. Blurry Images
**Problem:** Camera shake or motion blur makes text unreadable.

**Solutions:**
- Image sharpening filters
- Deblur algorithms
- Request retake

**UX Handling:**
```typescript
if (blurDetected) {
  showMessage("The image appears blurry. Please take a clear, steady photo.");
  showRetakeButton();
}
```

### 3. Angled/Curved Tickets
**Problem:** Ticket not flat, causing perspective distortion.

**Solutions:**
- Perspective correction (warp transform)
- Deskew algorithms
- Guide user to take photo from above

**UX Handling:**
```typescript
showGuidelines("Position your phone directly above the ticket, keeping it flat.");
```

### 4. Partial Parsing
**Problem:** OCR extracts some fields but misses others.

**UX Handling:**
```typescript
interface PartialParseResult {
  extracted: {
    fine_amount: true,
    offence_code: true,
    court_date: false  // Missing
  },
  confidence: 0.65
}

if (result.confidence < 0.8) {
  showPartialResults(result.extracted);
  showMessage("I couldn't read everything. Please confirm or edit the information below:");
  showEditableFields(result.extracted);
}
```

### 5. Handwritten Fields
**Problem:** Some tickets have handwritten notes that OCR can't read.

**UX Handling:**
```typescript
showMessage("Some fields appear to be handwritten. Please review and enter manually if needed.");
```

## Error Messages

### User-Friendly Messages

```typescript
const OCR_ERROR_MESSAGES = {
  low_confidence: "I couldn't read your ticket clearly. Please try:\n- Better lighting\n- Hold phone steady\n- Take photo from directly above",
  no_text_found: "I couldn't find any text in this image. Please make sure you're photographing the ticket.",
  partial_parse: "I read some information, but not everything. Please review and fill in any missing details.",
  blurry: "The image is too blurry. Please take a clear, steady photo.",
  too_dark: "The image is too dark. Please try with better lighting.",
  wrong_orientation: "The ticket appears sideways. Please rotate and try again."
};
```

## Fallback Options

### 1. Manual Entry
If OCR fails, offer manual form:
- Offence code
- Fine amount
- Court date
- Location
- etc.

### 2. Retake Photo
Always provide option to retake with guidance.

### 3. Upload Alternative
Allow user to upload a scanned PDF instead of photo.

## Testing Checklist

- [ ] Low light photos
- [ ] Blurry images
- [ ] Angled photos
- [ ] Handwritten text
- [ ] Different ticket formats
- [ ] Different jurisdictions
- [ ] Old/faded tickets
- [ ] Folded/creased tickets
- [ ] Glare/reflection
- [ ] Multiple tickets in one photo

## Implementation Example

```python
def process_ticket_image(image_path: str) -> Dict:
    """
    Process ticket image with error handling.
    """
    # Pre-process
    image = preprocess_image(image_path)
    
    # Check quality
    quality_score = assess_image_quality(image)
    if quality_score < 0.5:
        return {
            "success": False,
            "error": "low_quality",
            "message": "Image quality is too low. Please retake with better lighting."
        }
    
    # OCR
    ocr_result = run_ocr(image)
    
    # Check confidence
    if ocr_result.confidence < 0.7:
        return {
            "success": False,
            "error": "low_confidence",
            "message": "Couldn't read ticket clearly. Please try again.",
            "partial_data": ocr_result.partial_data
        }
    
    # Parse
    parsed = parse_ticket(ocr_result.text)
    
    # Validate
    if not parsed.is_complete():
        return {
            "success": "partial",
            "data": parsed,
            "message": "Read some information. Please review and complete missing fields."
        }
    
    return {
        "success": True,
        "data": parsed
    }
```

