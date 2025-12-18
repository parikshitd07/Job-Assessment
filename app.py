"""
Flask API for SHL Assessment Recommendation System
UPDATED: Now uses LLM-integrated recommendation engine
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from llm_recommendation_engine import LLMRecommendationEngine
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize LLM recommendation engine
print("Initializing LLM-based recommendation engine...")
print("This uses: Gemini Pro API + Sentence Transformers")
try:
    engine = LLMRecommendationEngine('shl_full_catalog.json')
    print("✓ LLM Recommendation engine ready!")
except Exception as e:
    print(f"⚠ Fallback: Using smaller dataset - {str(e)[:50]}")
    engine = LLMRecommendationEngine('assessments_data.json')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'SHL Assessment Recommendation API is running'
    }), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    """Assessment recommendation endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query'
            }), 400
        
        query = data['query']
        
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return jsonify({
                'error': 'Query must be a non-empty string'
            }), 400
        
        # Get number of recommendations (default 10, min 1, max 10)
        top_k = data.get('top_k', 10)
        top_k = max(1, min(10, int(top_k)))
        
        # Get recommendations using LLM engine
        recommendations = engine.recommend(query, top_k=top_k)
        formatted_recommendations = engine.format_for_api(recommendations)
        
        # Format response according to EXACT API specification
        response = {
            'recommended_assessments': [
                {
                    'url': rec['assessment_url'],
                    'name': rec['assessment_name'],
                    'adaptive_support': rec['adaptive_support'],
                    'description': rec['description'],
                    'duration': rec['duration'],
                    'remote_support': rec['remote_support'],
                    'test_type': [rec['test_type']] if rec['test_type'] else []
                }
                for rec in formatted_recommendations
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Serve the frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/api', methods=['GET'])
def api_info():
    """API info endpoint"""
    return jsonify({
        'message': 'SHL Assessment Recommendation API',
        'version': '1.0',
        'endpoints': {
            '/health': 'GET - Health check',
            '/recommend': 'POST - Get assessment recommendations'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
