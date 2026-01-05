# Quick Cost Comparison: OpenAI Models

## 💰 Cost Per Question (Average)

| Model | Cost Per Question | Monthly (100 Q/day) | Monthly (1000 Q/day) |
|-------|------------------|---------------------|----------------------|
| **GPT-4o** (current) | ~$0.0075 | **$22.50** 💸 | **$225** 💸💸💸 |
| **GPT-4o-mini** ⭐ | ~$0.00045 | **$1.35** ✅ | **$13.50** ✅ |
| **GPT-3.5-turbo** | ~$0.00125 | **$3.75** ✅ | **$37.50** ✅ |
| **Ollama** 🎉 | **$0.00** | **$0** 🎉 | **$0** 🎉 |

## 🎯 Recommendation

**Switch to GPT-4o-mini** - 94% cheaper, still great quality!

Just change in `.env`:
```env
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Or use **Ollama** for 100% free (no API key needed):
```env
LLM_PROVIDER=ollama
```

## 📊 Savings

- **GPT-4o → GPT-4o-mini**: Save **$21/month** (100 Q/day)
- **GPT-4o → Ollama**: Save **$22.50/month** (100 Q/day)

See `OPENAI_COST_CALCULATOR.md` for detailed breakdown!
