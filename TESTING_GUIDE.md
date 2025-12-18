# Testing Guide - SHL Assessment Recommendation System

## How to Test the Application?

This guide covers all testing methods for the SHL Assessment Recommendation System.

---

## 🚀 Quick Test (API is Already Running)

Since the API is already running on `localhost:5000`, you can test immediately:

### Test 1: Health Check
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "SHL Assessment Recommendation API is running"
}
```

### Test 2: Get Recommendations
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"I am hiring for Java developers who can also collaborate effectively"}'
```

**Expected Response:**
```json
{
  "query": "I am hiring for Java developers...",
  "recommendations": [
    {
      "assessment_name": "Java 8 New",
      "assessment_url": "https://www.shl.com/...",
      "description": "...",
      "duration": 0,
      "test_type": "K"
    }
  ]
}
```

---

## Method 1: Using the Web Interface (Easiest)

### Step 1: Open Browser
```bash
open http://localhost:5000
# Or manually navigate to: http://localhost:5000
```

### Step 2: Test Queries

Try these example queries in the web interface:

1. **Java Developer**:
   ```
   I am hiring for Java developers who can also collaborate effectively with my business teams
   ```

2. **Data Analyst**:
   ```
   Senior Data Analyst with SQL, Python and Excel expertise
   ```

3. **Sales Position**:
   ```
   Entry level sales position for new graduates
   ```

4. **Marketing Manager**:
   ```
   Marketing Manager with communication skills and leadership experience
   ```

### Step 3: Verify Results
- Should see 5-10 assessment recommendations
- Each with name, URL, and details
- Should load within 2-3 seconds

---

## Method 2: Using curl (Command Line)

### Test Health Endpoint
```bash
curl http://localhost:5000/health
```

### Test Recommendation Endpoint - Example 1
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need a Java developer",
    "top_k": 5
  }'
```

### Test Recommendation Endpoint - Example 2
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Looking for Python developers with SQL and data analysis skills"
  }'
```

### Test Recommendation Endpoint - Example 3 (Job Description)
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "We are hiring a QA Engineer with experience in Selenium, Java, JavaScript, and SQL Server. Strong communication skills required."
  }'
```

---

## Method 3: Using Python test_api.py

### Run the Test Script
```bash
cd ""
python3 test_api.py
```

This will automatically test:
- Health endpoint
- Multiple recommendation queries
- Response format validation
- Timing

**Expected Output:**
```
Testing Health Endpoint...
✓ Health check passed

Testing Recommendation Endpoint...
Query: Java developer...
✓ Got 5 recommendations
✓ Response time: 0.5s

All tests passed!
```

---

## Method 4: Testing Individual Components

### Test 1: Recommendation Engine Only
```bash
python3 llm_recommendation_engine.py
```

**What it tests**:
- LLM initialization (Gemini API)
- Assessment data loading
- Embedding/TF-IDF index building
- Sample recommendations

**Expected Output**:
```
✓ Gemini API initialized
✓ Loaded 54 assessments
Using TF-IDF vectorizer...
✓ Built TF-IDF index

Query: Java developer...
→ Retrieved 30 candidates
✓ Final: 5 recommendations

Top 5 recommendations:
1. Java 8 New
2. Core Java Advanced Level
...
```

### Test 2: Evaluation Metrics
```bash
python3 evaluate.py
```

**What it tests**:
- Loads training data
- Runs recommendations on all queries
- Calculates Mean Recall@10

**Expected Output**:
```
Evaluating on 10 training queries...

Query 1: Java developers...
  Predicted: 10 assessments
  Ground truth: 5 assessments
  Recall@10: 0.60

...

Mean Recall@10: 0.3967
```

### Test 3: Test Prediction Generation
```bash
python3 generate_predictions.py
```

**What it tests**:
- Loads test queries
- Generates recommendations
- Saves to CSV

**Expected Output**:
```
Generating predictions for 9 test queries...

Query 1: Looking to hire mid-level...
  ✓ Generated 10 recommendations

...

✓ Saved predictions to test_predictions.csv
```

---

## Method 5: Testing with Different Configurations

### Test Without Gemini API Key
```bash
# Unset API key to test fallback
unset GEMINI_API_KEY
python3 app.py
```

**Expected**: Should work but show:
```
⚠ Gemini API not available, using fallback
```

### Test With Gemini API Key
```bash
export GEMINI_API_KEY="your_key_here"
python3 app.py
```

**Expected**: Should show:
```
✓ Gemini API initialized
```

---

## Method 6: Browser Developer Tools Testing

### Step 1: Open browser to http://localhost:5000

### Step 2: Open Developer Tools (F12)

### Step 3: Go to Network Tab

### Step 4: Submit a query

### Step 5: Inspect the Response
- Should see POST to `/recommend`
- Status: 200 OK
- Response time: < 3 seconds
- Response body: JSON with recommendations

---

## Method 7: Load Testing (Optional)

### Simple Load Test
```bash
# Install Apache Bench (usually pre-installed on Mac)
# Test 100 requests, 10 concurrent
ab -n 100 -c 10 -p query.json -T application/json http://localhost:5000/recommend
```

Create `query.json`:
```json
{"query":"Java developer"}
```

---

## 🧪 Test Checklist

### Basic Functionality:
- [ ] Health endpoint returns 200 OK
- [ ] Recommendation endpoint returns JSON
- [ ] Web interface loads correctly
- [ ] Can submit queries via web interface
- [ ] Recommendations appear within 3 seconds

### Data Quality:
- [ ] Recommendations are relevant to query
- [ ] At least 5 recommendations returned
- [ ] Assessment URLs are valid
- [ ] Assessment names are descriptive

### Error Handling:
- [ ] Empty query returns error
- [ ] Invalid JSON returns 400 error
- [ ] Missing 'query' field returns error
- [ ] System handles large queries (>1000 chars)

### Performance:
- [ ] Response time < 3 seconds
- [ ] Can handle 10 concurrent requests
- [ ] Memory usage stable

### LLM Integration (if API key set):
- [ ] Shows "✓ Gemini API initialized"
- [ ] Query understanding works
- [ ] Re-ranking improves results

---

## 📊 Verifying Test Results

### Good Results Look Like:

**For "Java developer" query**:
```
✓ Returns Java-related assessments
✓ Includes technical tests
✓ May include soft skills if query mentions them
✓ Response time < 2 seconds
```

**For "Sales position" query**:
```
✓ Returns sales-related assessments
✓ Includes personality/behavioral tests
✓ May include communication tests
✓ Response time < 2 seconds
```

---

## 🔧 Troubleshooting Tests

### Issue: "Connection refused"
**Solution**: Make sure API is running:
```bash
python3 app.py
```

### Issue: "No recommendations returned"
**Solution**: Check if assessment data loaded:
```bash
ls -lh shl_full_catalog.json assessments_data.json
```

### Issue: "Slow responses"
**Solution**: 
- Check if embeddings are building (first time is slow)
- Verify system resources
- Try with smaller dataset

### Issue: "LLM not working"
**Solution**: 
- Verify GEMINI_API_KEY is set
- Check API key is valid
- System works without LLM (fallback mode)

---

## 🎯 Quick Test Commands

```bash
# Complete test suite
./run_all_tests.sh

# Or manually:
echo "1. Testing health..."
curl http://localhost:5000/health

echo "\n2. Testing recommendation..."
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"Java developer"}'

echo "\n3. Testing evaluation..."
python3 evaluate.py

echo "\n4. Testing components..."
python3 llm_recommendation_engine.py

echo "\nAll tests complete!"
```

---

## Expected Results Summary

| Test | Expected Result | Time |
|------|----------------|------|
| Health Check | 200 OK | < 100ms |
| Recommendation | 5-10 results | < 3s |
| Web Interface | Loads correctly | < 1s |
| Evaluation | Mean Recall~0.40 | ~30s |
| Component Test | No errors | ~10s |

---

## For Assignment Evaluation

The evaluators will test:
1. ✅ API `/health` endpoint
2. ✅ API `/recommend` endpoint with sample queries
3. ✅ Response format matches specification
4. ✅ Web interface functionality
5. ✅ Code quality and documentation

**All tests should pass!** ✅
