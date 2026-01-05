# Evaluation & Testing

This folder contains evaluation datasets and testing scripts to verify system accuracy.

## 📁 Structure

```
evaluation/
├── test_cases/              # Test cases with expected outputs
│   ├── ontario_tickets.json
│   └── california_tickets.json
├── scripts/                 # Evaluation scripts
│   ├── run_evaluation.py
│   └── compare_results.py
└── results/                 # Evaluation results
    └── latest_results.json
```

## 🎯 Test Case Format

Each test case includes:
- Input: Ticket data + question
- Expected: Key points that should appear in answer
- Metrics: What to check (offence identified, demerit points, options presented)

## 📊 Evaluation Metrics

1. **Offence Identification**: Did it correctly identify the offence?
2. **Demerit Points**: Were points correctly stated?
3. **Options Presented**: Were FIGHT and PAY options both provided?
4. **Accuracy**: Were legal facts correct?
5. **Completeness**: Were all important points covered?

## 🚀 Running Evaluation

```bash
cd evaluation/scripts
python run_evaluation.py
```

This will:
1. Load test cases
2. Run queries through the system
3. Compare outputs to expected results
4. Generate a report

