# Legal Category Mapping System

## Overview

This document maps your legal dataset to standardized legal categories based on Canadian and US legal systems, as outlined in your legal framework.

---

## 🇨🇦 Canada Legal Categories (7 Categories)

### 1. Constitutional Law
**Keywords**: constitution, charter, rights, freedoms, constitutional

**Subcategories**:
- Constitutional Law
- Charter Rights
- Division of Powers

**Your Data Mapping**:
- Documents mentioning "Charter of Rights and Freedoms"
- Constitutional documents
- Federal vs provincial jurisdiction documents

**Priority**: Medium (for your app)

---

### 2. Criminal Law
**Keywords**: criminal, criminal code, offence, assault, theft, fraud, dui, impaired, drug, homicide, robbery

**Subcategories**:
- Criminal Law
- Criminal Code
- Federal Criminal
- Provincial Criminal

**Your Data Mapping**:
- `canada_criminal_law/` directory
- `canada criminal and federal law/` directory
- Documents with "Criminal Code of Canada"
- DUI/Impaired driving documents

**Priority**: High (for DUI/hybrid cases)

---

### 3. Administrative Law
**Keywords**: administrative, tribunal, immigration, licensing, professional, employment insurance, appeal, agency, regulatory

**Subcategories**:
- Administrative Law
- Immigration
- Licensing
- Tribunals

**Your Data Mapping**:
- Immigration documents
- Professional licensing documents
- Tribunal decisions
- Regulatory agency documents

**Priority**: High (for appeals, tribunals)

---

### 4. Civil Law (Private Law)
**Keywords**: civil, contract, tort, negligence, personal injury, property dispute, debt, collection, civil code, quebec civil

**Subcategories**:
- Contract Law
- Tort Law
- Property Disputes
- Debt Collections

**Your Data Mapping**:
- Contract law documents
- Tort/negligence documents
- Property dispute documents
- Quebec Civil Code documents

**Priority**: Medium (for small disputes)

---

### 5. Family Law
**Keywords**: family, divorce, custody, child support, spousal support, marriage, adoption, separation

**Subcategories**:
- Divorce
- Custody
- Support
- Adoption

**Your Data Mapping**:
- Divorce law documents
- Family law documents
- Child custody documents

**Priority**: Low (not needed for now)

---

### 6. Property & Real Estate Law
**Keywords**: property, real estate, mortgage, landlord, tenant, eviction, zoning, land ownership

**Subcategories**:
- Real Estate
- Landlord Tenant
- Mortgages
- Zoning

**Your Data Mapping**:
- Property law documents
- Real estate documents
- Landlord-tenant documents

**Priority**: Low (for now)

---

### 7. Regulatory / Traffic Law ⭐ **CORE FOR YOUR APP**
**Keywords**: traffic, highway, motor vehicle, speeding, parking, ticket, demerit, provincial offences, bylaw, traffic act, highway traffic, regulatory, traffic violation

**Subcategories**:
- Traffic Law
- Provincial Offences
- Parking
- Speeding
- DUI Traffic (hybrid)

**Your Data Mapping**:
- `CANADA TRAFFIC FILES/` directory
- `canada_traffic_acts/` directory
- Documents with "Highway Traffic Act"
- Demerit point tables
- Traffic ticket documents

**Priority**: **HIGHEST** (core use case)

---

## 🇺🇸 USA Legal Categories (9 Categories)

### 1. Constitutional Law
**Keywords**: constitution, constitutional, bill of rights, due process, equal protection, amendment

**Subcategories**:
- Constitutional Law
- Bill of Rights
- State Constitutions

**Your Data Mapping**:
- US Constitution documents
- Bill of Rights documents
- State constitution documents

**Priority**: Medium

---

### 2. Criminal Law
**Keywords**: criminal, felony, misdemeanor, offense, assault, theft, fraud, homicide, robbery, drug, firearms

**Subcategories**:
- Federal Criminal
- State Criminal
- Felonies
- Misdemeanors

**Your Data Mapping**:
- `usa_criminal_law/` directory
- Federal criminal code documents
- State criminal code documents

**Priority**: High (for DUI/hybrid cases)

---

### 3. Civil Law
**Keywords**: civil, contract, tort, negligence, personal injury, business dispute, consumer protection, civil code

**Subcategories**:
- Contracts
- Torts
- Business Disputes
- Consumer Protection

**Your Data Mapping**:
- Civil law documents
- Contract law documents
- Tort law documents

**Priority**: Medium (for small disputes)

---

### 4. Administrative Law
**Keywords**: administrative, agency, immigration, social security, environmental, regulatory, federal agency, state agency

**Subcategories**:
- Immigration
- Social Security
- Environmental
- Agencies

**Your Data Mapping**:
- Immigration documents
- Administrative agency documents
- Regulatory documents

**Priority**: High (for appeals, tribunals)

---

### 5. Family Law
**Keywords**: family, divorce, custody, child support, spousal support, marriage, adoption

**Subcategories**:
- Divorce
- Custody
- Support
- Adoption

**Your Data Mapping**:
- Family law documents
- Divorce law documents

**Priority**: Low (not needed for now)

---

### 6. Property & Real Estate Law
**Keywords**: property, real estate, zoning, land ownership, eviction, mortgage, landlord, tenant

**Subcategories**:
- Real Estate
- Zoning
- Landlord Tenant
- Evictions

**Your Data Mapping**:
- Property law documents
- Real estate documents

**Priority**: Low (for now)

---

### 7. Regulatory / Traffic Law ⭐ **CORE FOR YOUR APP**
**Keywords**: traffic, highway, motor vehicle, speeding, parking, ticket, traffic violation, traffic court, municipal court, dui

**Subcategories**:
- Traffic Law
- Traffic Tickets
- Speeding
- Parking
- DUI Traffic (hybrid)

**Your Data Mapping**:
- `us_traffic_laws/` directory
- `us_state_codes/` directory (traffic sections)
- Traffic ticket documents
- State traffic code documents

**Priority**: **HIGHEST** (core use case)

---

### 8. Tax Law
**Keywords**: tax, irs, income tax, state tax, tax code, taxation

**Subcategories**:
- Federal Tax
- State Tax
- IRS Rules

**Your Data Mapping**:
- Tax law documents
- IRS documents

**Priority**: Low (not needed for now)

---

### 9. Employment & Labor Law
**Keywords**: employment, labor, labour, worker rights, discrimination, union, employment law, labor law

**Subcategories**:
- Worker Rights
- Discrimination
- Unions
- Employment Law

**Your Data Mapping**:
- Employment law documents
- Labor law documents

**Priority**: Low (not needed for now)

---

## 🎯 Priority Categories for Your App

Based on your use case (tickets, summons, paralegal advice), here's the priority order:

| Priority | Category | Why |
|----------|----------|-----|
| **1** | Regulatory / Traffic | Core use case - tickets, violations |
| **2** | Administrative | Appeals, tribunals, licensing |
| **3** | Criminal (light) | DUI / hybrid cases |
| **4** | Civil (small) | Fines, small disputes |
| 5 | Constitutional | Rights issues |
| 6 | Property | Real estate disputes |
| 7 | Family | Not needed for now |
| 8 | Tax | Not needed for now |
| 9 | Employment | Not needed for now |

---

## 📊 Your Current Data Structure Mapping

### Canada Data
```
canada_traffic_acts/          → regulatory_traffic
CANADA TRAFFIC FILES/         → regulatory_traffic
canada_criminal_law/          → criminal
canada criminal and federal law/ → criminal, constitutional
canada_case_law/              → case_law (with category context)
```

### USA Data
```
us_traffic_laws/              → regulatory_traffic
us_state_codes/               → regulatory_traffic, criminal, civil (mixed)
usa_criminal_law/             → criminal
usa_case_law/                 → case_law (with category context)
```

### Mixed/General Data
```
data/downloaded_pdfs/         → Various (needs classification)
docs/downloaded_pdfs/         → Various (needs classification)
```

---

## 🔧 Implementation

The `legal_category_mapper.py` script provides:

1. **Automatic Classification**: Analyzes file paths and names to determine category
2. **Jurisdiction Detection**: Identifies Canada vs USA documents
3. **Priority Scoring**: Ranks documents by relevance to your app
4. **Tag Generation**: Creates searchable tags for filtering

### Usage Example:
```python
from legal_category_mapper import classify_legal_category, detect_jurisdiction

file_path = Path('canada_traffic_acts/ontario_highway_traffic_act.pdf')
jurisdiction = detect_jurisdiction(file_path)
category, subcategory, tags = classify_legal_category(file_path, jurisdiction)

print(f"Category: {category}")
print(f"Subcategory: {subcategory}")
print(f"Tags: {tags}")
```

---

## 📈 Next Steps

1. **Run Category Analysis**: Use `legal_category_mapper.py` to analyze all your documents
2. **Update Ingestion Script**: Integrate category mapping into `ingest_all_documents.py`
3. **Filter by Priority**: Focus ingestion on high-priority categories first
4. **UI Category Selector**: Build a category selector in your frontend that adapts chatbot behavior

---

## 🚀 Benefits

✅ **Structured Organization**: All documents properly categorized  
✅ **Smart Filtering**: Filter by category, jurisdiction, priority  
✅ **Focused RAG**: Prioritize high-relevance documents in search  
✅ **Better UX**: Users can select legal category for context-aware responses  
✅ **Scalable**: Easy to add new categories or subcategories
