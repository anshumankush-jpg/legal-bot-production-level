# Quick Legal Category Guide

## 🚀 Quick Start

### 1. Analyze Your Documents
```bash
python analyze_legal_categories.py
```

This will:
- ✅ Scan all your legal documents
- ✅ Categorize them by legal type (Constitutional, Criminal, Traffic, etc.)
- ✅ Show breakdown by jurisdiction (Canada vs USA)
- ✅ Identify high-priority documents for your app
- ✅ Generate a detailed report

### 2. Use Enhanced Ingestion
```bash
python ingest_all_documents.py
```

Now automatically:
- ✅ Uses legal category mapper for better classification
- ✅ Adds category metadata (jurisdiction, subcategory, tags, priority)
- ✅ Prioritizes high-value documents

---

## 📋 Category Quick Reference

### High Priority (Your Core Use Case) ⭐

| Category | What It Covers | Your Data |
|----------|----------------|-----------|
| **Regulatory / Traffic** | Tickets, speeding, parking, DUI traffic | `CANADA TRAFFIC FILES/`, `us_traffic_laws/` |
| **Administrative** | Appeals, tribunals, licensing | Immigration docs, tribunal decisions |
| **Criminal (light)** | DUI, hybrid cases | `canada_criminal_law/`, `usa_criminal_law/` |
| **Civil (small)** | Small disputes, fines | Contract, tort documents |

### Medium Priority

| Category | What It Covers |
|----------|----------------|
| **Constitutional** | Rights, freedoms, Charter |
| **Property** | Real estate, landlord-tenant |

### Low Priority (Not Needed for Now)

| Category | What It Covers |
|----------|----------------|
| **Family** | Divorce, custody |
| **Tax** | Tax law |
| **Employment** | Labor law |

---

## 🔧 Code Examples

### Classify a Single Document
```python
from pathlib import Path
from legal_category_mapper import classify_legal_category, detect_jurisdiction

file_path = Path('canada_traffic_acts/ontario_highway_traffic_act.pdf')
jurisdiction = detect_jurisdiction(file_path)
category, subcategory, tags = classify_legal_category(file_path, jurisdiction)

print(f"Category: {category}")
print(f"Subcategory: {subcategory}")
print(f"Tags: {tags}")
```

### Batch Categorize Documents
```python
from pathlib import Path
from legal_category_mapper import categorize_document_batch

documents = [
    Path('canada_traffic_acts/ontario_highway_traffic_act.pdf'),
    Path('usa_criminal_law/federal_criminal_code.pdf'),
]

results = categorize_document_batch(documents)

for file_path, info in results.items():
    print(f"{Path(file_path).name}: {info['category_display']} [{info['jurisdiction']}]")
```

### Filter by Priority
```python
from legal_category_mapper import get_category_priority

# Get only high-priority documents
high_priority = [
    (path, info) for path, info in results.items()
    if info['is_high_priority']
]
```

---

## 📊 Understanding the Output

### Category Analysis Output
```
📁 BY LEGAL CATEGORY (Priority Order)
⭐ [0] Regulatory / Traffic Law      :  450 documents
⭐ [1] Administrative Law             :   85 documents
⭐ [2] Criminal Law                   :  120 documents
⭐ [3] Civil Law                      :   65 documents
  [5] Constitutional Law              :   25 documents
  [6] Property & Real Estate Law      :   15 documents
```

- **Priority 0-3**: High priority for your app ⭐
- **Priority 4+**: Lower priority (can ingest later)

### Metadata in Vector Store

Each document chunk now includes:
```python
{
    'legal_category': 'regulatory_traffic',
    'category_display': 'Regulatory / Traffic Law',
    'subcategory': 'traffic_law',
    'jurisdiction': 'canada',
    'category_tags': ['regulatory_traffic', 'traffic_law', 'canada', 'highway', 'traffic'],
    'category_priority': 0,
    'is_high_priority': True
}
```

---

## 🎯 Next Steps

1. **Run Analysis**: `python analyze_legal_categories.py`
2. **Review Report**: Check `legal_category_analysis.json`
3. **Ingest High-Priority First**: Focus on categories 0-3
4. **Update Frontend**: Add category selector to your UI
5. **Filter Queries**: Use category metadata to improve RAG results

---

## 💡 Tips

- **Traffic documents** are automatically classified as `regulatory_traffic` (highest priority)
- **Case law** inherits category from context (e.g., traffic case law → `regulatory_traffic`)
- **DUI documents** may be classified as both `criminal` and `regulatory_traffic` (hybrid)
- **Unknown documents** default to `general` category

---

## 🆘 Troubleshooting

**Q: Category mapper not found?**
```bash
# Make sure legal_category_mapper.py is in project root
ls legal_category_mapper.py
```

**Q: Documents not categorizing correctly?**
- Check file paths contain keywords (traffic, criminal, etc.)
- Review `LEGAL_CATEGORY_MAPPING.md` for keyword list
- Manually adjust keywords in `legal_category_mapper.py` if needed

**Q: Want to add new categories?**
- Edit `CANADA_CATEGORIES` or `USA_CATEGORIES` in `legal_category_mapper.py`
- Add keywords and subcategories
- Update `APP_PRIORITY_CATEGORIES` if needed
