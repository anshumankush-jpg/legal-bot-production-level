# OpenAI API Cost Calculator for PLAZA-AI

## 💰 Current OpenAI Pricing (as of January 2025)

### Small/Cheap Models (Recommended for Cost Savings)

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Best For |
|-------|---------------------------|----------------------------|----------|
| **GPT-3.5-turbo** | $0.50 | $1.50 | Budget-friendly, fast |
| **GPT-4o-mini** | $0.15 | $0.60 | **BEST VALUE** - New, cheap, good quality |
| **GPT-4o** | $2.50 | $10.00 | High quality (currently configured) |

### Current Configuration
Your system is set to use: **GPT-4o** (expensive!)
- Input: **$2.50 per 1M tokens**
- Output: **$10.00 per 1M tokens**

---

## 📊 Cost Examples

### Example 1: Single Legal Question
**Using GPT-4o (current):**
- Input: ~1,000 tokens (question + context) = **$0.0025**
- Output: ~500 tokens (answer) = **$0.005**
- **Total per question: ~$0.0075** (less than 1 cent)

**Using GPT-4o-mini (recommended):**
- Input: ~1,000 tokens = **$0.00015**
- Output: ~500 tokens = **$0.0003**
- **Total per question: ~$0.00045** (less than 0.05 cents)
- **Savings: 94% cheaper!**

**Using GPT-3.5-turbo:**
- Input: ~1,000 tokens = **$0.0005**
- Output: ~500 tokens = **$0.00075**
- **Total per question: ~$0.00125**
- **Savings: 83% cheaper!**

### Example 2: Daily Usage (100 questions/day)
**Using GPT-4o:**
- 100 questions × $0.0075 = **$0.75/day**
- Monthly: **~$22.50/month**

**Using GPT-4o-mini:**
- 100 questions × $0.00045 = **$0.045/day**
- Monthly: **~$1.35/month**
- **Savings: $21/month!**

**Using GPT-3.5-turbo:**
- 100 questions × $0.00125 = **$0.125/day**
- Monthly: **~$3.75/month**
- **Savings: $18.75/month!**

### Example 3: Heavy Usage (1,000 questions/day)
**Using GPT-4o:**
- 1,000 questions × $0.0075 = **$7.50/day**
- Monthly: **~$225/month** 💸

**Using GPT-4o-mini:**
- 1,000 questions × $0.00045 = **$0.45/day**
- Monthly: **~$13.50/month**
- **Savings: $211.50/month!** 🎉

---

## 🎯 Recommendation: Switch to GPT-4o-mini

**Why GPT-4o-mini?**
- ✅ **94% cheaper** than GPT-4o
- ✅ **Still high quality** (better than GPT-3.5)
- ✅ **Fast responses**
- ✅ **Same API format** (easy to switch)

### How to Switch

Update your `.env` file:
```env
# Change from:
OPENAI_CHAT_MODEL=gpt-4o

# To:
OPENAI_CHAT_MODEL=gpt-4o-mini
```

That's it! Restart your backend and you'll save 94% on costs!

---

## 💡 Cost Comparison Table

| Usage Level | GPT-4o | GPT-4o-mini | GPT-3.5-turbo | Savings (vs GPT-4o) |
|-------------|--------|-------------|---------------|---------------------|
| **10 questions/day** | $0.08/day | $0.005/day | $0.013/day | 94% (mini) / 84% (3.5) |
| **100 questions/day** | $0.75/day | $0.045/day | $0.125/day | 94% (mini) / 83% (3.5) |
| **1,000 questions/day** | $7.50/day | $0.45/day | $1.25/day | 94% (mini) / 83% (3.5) |
| **Monthly (100/day)** | **$22.50** | **$1.35** | **$3.75** | **$21.15** (mini) |

---

## 🔢 Token Estimation

**Average legal question:**
- User question: ~50-100 tokens
- System prompt: ~200 tokens
- Retrieved context: ~500-1,000 tokens
- **Total input: ~750-1,300 tokens**
- **Output: ~300-800 tokens**

**Your current config:**
- `OPENAI_MAX_TOKENS=2500` (output limit)
- This is fine, but you can reduce to 1500 to save more

---

## 📝 Quick Cost Calculator

To estimate your costs:
1. Count your questions per day
2. Estimate tokens per question (input + output)
3. Use the pricing table above

**Formula:**
```
Daily Cost = (Questions × Input Tokens × Input Price) + (Questions × Output Tokens × Output Price)
```

**Example (100 questions, 1000 input + 500 output tokens):**
- GPT-4o: (100 × 0.001 × $2.50) + (100 × 0.0005 × $10.00) = $0.25 + $0.50 = **$0.75/day**
- GPT-4o-mini: (100 × 0.001 × $0.15) + (100 × 0.0005 × $0.60) = $0.015 + $0.03 = **$0.045/day**

---

## ⚠️ Important Notes

1. **Embeddings are separate**: Your system uses local embeddings (Sentence Transformers), so no embedding costs!

2. **Free tier**: OpenAI gives $5 free credit to new accounts (enough for ~700 GPT-4o-mini questions)

3. **Rate limits**: Free tier has rate limits, paid accounts have higher limits

4. **Billing**: OpenAI bills per token used, not per request

---

## 🎯 Action Items

1. **Switch to GPT-4o-mini** (save 94%)
   ```env
   OPENAI_CHAT_MODEL=gpt-4o-mini
   ```

2. **Or use free Ollama** (save 100%!)
   ```env
   LLM_PROVIDER=ollama
   ```

3. **Reduce max_tokens** if you want (optional)
   ```env
   OPENAI_MAX_TOKENS=1500  # Instead of 2500
   ```

---

## 💰 Summary

- **Current (GPT-4o)**: ~$0.0075 per question
- **Recommended (GPT-4o-mini)**: ~$0.00045 per question (**94% savings!**)
- **Free (Ollama)**: $0.00 per question (**100% savings!**)

**For 100 questions/day:**
- GPT-4o: **$22.50/month**
- GPT-4o-mini: **$1.35/month** ⭐
- Ollama: **$0/month** 🎉

Choose based on your budget and quality needs!
