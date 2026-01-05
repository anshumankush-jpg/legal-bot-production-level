# 📝 Sample Questions for Artillity

Based on the sample data files, here are questions you can ask Artillity to test the search functionality.

---

## 🏥 Healthcare AI Questions

**Sample File**: `sample_data/sample_texts.txt`

### Questions to Try:
1. **"What is artificial intelligence in healthcare?"**
   - Expected: Information about AI transforming healthcare

2. **"How does machine learning help with medical imaging?"**
   - Expected: Details about AI detecting anomalies in X-rays, MRIs

3. **"What are the applications of AI in patient care?"**
   - Expected: Predictive analytics, virtual assistants, remote monitoring

4. **"How does AI help with drug discovery?"**
   - Expected: Information about accelerating pharmaceutical research

5. **"What is personalized medicine?"**
   - Expected: AI enabling personalized treatment plans

---

## 💻 Technology Questions

**Sample File**: `sample_data/tech_articles.txt`

### Questions to Try:
1. **"What is machine learning?"**
   - Expected: Explanation of ML fundamentals

2. **"How does deep learning work?"**
   - Expected: Information about neural networks

3. **"What is natural language processing?"**
   - Expected: NLP explanation and applications

4. **"What are computer vision applications?"**
   - Expected: Image recognition, facial recognition uses

5. **"What is the future of AI technology?"**
   - Expected: Future possibilities and AGI

---

## 🛒 Product Questions

**Sample File**: `sample_data/products.csv`

### Questions to Try:
1. **"What electronics products do you have?"**
   - Expected: List of electronics (laptops, smartphones, tablets)

2. **"Show me products under $500"**
   - Expected: Tablets, accessories, etc.

3. **"What gaming products are available?"**
   - Expected: Gaming mouse, mechanical keyboard

4. **"Do you have any wearables?"**
   - Expected: Smart Watch

5. **"What accessories are available?"**
   - Expected: Laptop stand, mouse pad, cable organizer

---

## ❓ FAQ Questions

**Sample File**: `sample_data/faq_document.txt`

### Questions to Try:
1. **"What is an embedding?"**
   - Expected: Explanation of embeddings

2. **"How does the embedding server work?"**
   - Expected: How the server converts content to vectors

3. **"How fast is the search?"**
   - Expected: 1-2ms query time information

4. **"Is the service free?"**
   - Expected: Yes, uses open-source models

5. **"Can I search across different content types?"**
   - Expected: Yes, unified search across all types

6. **"How accurate is the search?"**
   - Expected: 40% retrieval accuracy

7. **"Do I need internet?"**
   - Expected: No, works offline

---

## 🏥 Healthcare Data Questions

**Sample File**: `sample_data/healthcare_data.csv`

### Questions to Try:
1. **"What treatments are available for diabetes?"**
   - Expected: Insulin therapy, diet and exercise

2. **"What are the patient outcomes?"**
   - Expected: Improved, stable outcomes

3. **"What conditions are treated?"**
   - Expected: Hypertension, diabetes, asthma, etc.

---

## 🔍 General Search Questions

### Questions That Work Across All Files:
1. **"artificial intelligence"**
   - Should find: Healthcare AI articles, tech articles, FAQ

2. **"machine learning"**
   - Should find: Tech articles, healthcare AI articles

3. **"technology"**
   - Should find: Tech articles, product catalog

4. **"healthcare"**
   - Should find: Healthcare AI articles, healthcare data

---

## 💡 Tips for Best Results

1. **Be Specific**: More specific questions get better results
   - ✅ Good: "How does AI help with medical imaging?"
   - ❌ Vague: "AI"

2. **Use Keywords**: Include key terms from your documents
   - ✅ Good: "artificial intelligence healthcare"
   - ❌ Less effective: "stuff about computers"

3. **Ask Natural Questions**: The system understands natural language
   - ✅ Good: "What products do you have?"
   - ✅ Good: "How does embedding work?"

4. **Try Different Phrasings**: If one doesn't work, rephrase
   - "AI in healthcare" vs "artificial intelligence healthcare"

---

## 🎯 Expected Answer Format

When you ask a question, Artillity will return:

1. **Top 3 Results** (by default)
2. **Preview Text** - Snippet from the document
3. **Source File** - Which file the answer came from
4. **Similarity Score** - How relevant the result is (0-1)

Example Response:
```
Result 1
Artificial intelligence is revolutionizing healthcare by enabling faster diagnosis...
[source: sample_data/sample_texts.txt]

Result 2
Machine learning algorithms can analyze medical images...
[source: sample_data/sample_texts.txt]

Artillity • 3 hit(s)
```

---

## 🚀 Quick Test Questions

Try these first to verify everything works:

1. **"What is artificial intelligence?"**
2. **"How does embedding work?"**
3. **"What products are available?"**

If these work, the system is connected and ready!

---

**Happy Searching!** 🔍

