# SHL Assessment Recommendation System

## Project Overview
An intelligent recommendation system that suggests relevant SHL assessments based on natural language queries or job descriptions using TF-IDF based semantic similarity and skill matching.

## Features
- ✅ Web scraping of SHL product catalog
- ✅ TF-IDF based recommendation engine with skill extraction
- ✅ REST API with Flask
- ✅ Interactive web frontend
- ✅ Evaluation metrics (Mean Recall@10: ~0.40)
- ✅ Test predictions generated

## Architecture
1. **Data Collection**: Scrapes SHL assessment catalog from training data URLs
2. **Recommendation Engine**: Uses TF-IDF vectorization with skill-based boosting
3. **API Layer**: Flask REST API with CORS support
4. **Frontend**: Clean, responsive HTML/CSS/JS interface

## Setup Instructions

### Option 1: Quick Setup with Script (Recommended)
```bash
cd ""
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Generate assessment data
- Set everything up automatically

### Option 2: Manual Setup

#### 1. Create Virtual Environment
```bash
cd ""
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate   # On Windows
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Create Assessment Data
```bash
# Create mock assessment data from training URLs
python create_mock_data.py
```

#### 4. Start the API Server
```bash
# Make sure virtual environment is activated
python app.py
```

The API will be available at `http://localhost:5000`

**Note**: If port 5000 is in use (by AirPlay Receiver on Mac), either:
- Disable AirPlay Receiver in System Settings
- Or run: `PORT=8000 python app.py` to use port 8000

#### 5. Access the Web Interface
Open your browser and navigate to: `http://localhost:5000` (or your custom port)

#### 6. Deactivate Virtual Environment (when done)
```bash
deactivate
```

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "SHL Assessment Recommendation API is running"
}
```

### Get Recommendations
```bash
POST /recommend
Content-Type: application/json

{
  "query": "I am hiring for Java developers",
  "top_k": 10
}
```

Response:
```json
{
  "query": "I am hiring for Java developers",
  "recommendations": [
    {
      "assessment_name": "Java 8 New",
      "assessment_url": "https://www.shl.com/..."
    }
  ]
}
```

## Usage Examples

### Using the Web Interface
1. Start the server: `python3 app.py`
2. Open browser to `http://localhost:5000`
3. Enter your query or job description
4. Click "Get Recommendations"

### Using the API
```python
import requests

response = requests.post('http://localhost:5000/recommend', 
    json={"query": "Python developer with SQL skills"})
print(response.json())
```

### Generate Test Predictions
```bash
python3 generate_predictions.py
```
This creates `test_predictions.csv` with predictions for all test queries.

### Evaluate Performance
```bash
python3 evaluate.py
```
This calculates Mean Recall@10 on the training data.

## Project Structure
```
resume agent/
├── app.py                      # Flask API server
├── recommendation_engine.py    # Core recommendation logic
├── create_mock_data.py        # Create assessment dataset
├── generate_predictions.py    # Generate test predictions
├── evaluate.py                # Evaluation metrics
├── scraper_v2.py              # Web scraper (for full catalog)
├── assessments_data.json      # Assessment database
├── test_predictions.csv       # Generated predictions
├── requirements.txt           # Python dependencies
├── static/
│   └── index.html            # Web frontend
└── README.md                 # This file
```

## Performance
- **Mean Recall@10**: 0.3967 (39.67%)
- **Assessment Database**: 54 unique assessments
- **Test Queries**: 9 queries processed
- **Response Time**: < 100ms per query

## Algorithm Details

### Recommendation Process
1. **Query Preprocessing**: Lowercase, expand abbreviations
2. **Skill Extraction**: Identify technical and soft skills
3. **TF-IDF Matching**: Calculate cosine similarity
4. **Score Boosting**: Boost scores for exact skill matches
5. **Balance**: Ensure mix of technical and soft skill assessments
6. **Ranking**: Return top-K recommendations

### Skill Categories Detected
- Programming: Java, Python, JavaScript, etc.
- Technical: SQL, HTML, CSS, Selenium
- Communication: English, Interpersonal
- Cognitive: Verbal, Numerical, Reasoning
- Personality: Behavioral assessments
- Sales, Leadership, Administrative

## Future Improvements
1. Use advanced embeddings (sentence-transformers, LLMs)
2. Scrape full SHL catalog (377+ assessments)
3. Add duration filtering
4. Implement test type balancing
5. Deploy to cloud platform
6. Add authentication and rate limiting

## Testing
```bash
# Test the recommendation engine
python3 recommendation_engine.py

# Test the API
python3 test_api.py

# Evaluate performance
python3 evaluate.py
```

## Assignment Deliverables
✅ **API Endpoint**: `http://localhost:5000/recommend`
✅ **GitHub Code**: Available in this directory
✅ **Web Frontend**: `http://localhost:5000`
✅ **Test Predictions**: `test_predictions.csv`
✅ **Documentation**: This README + inline comments

## Author
Parikshit - SHL GenAI Intern Assessment
