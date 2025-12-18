"""
Test the Flask API endpoints
"""
import requests
import json
import time

def test_health():
    """Test the health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_recommend():
    """Test the recommend endpoint"""
    print("\n\nTesting /recommend endpoint...")
    
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams",
        "Senior Data Analyst with SQL, Python and Excel expertise",
        "Entry level sales position"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        try:
            payload = {
                "query": query,
                "top_k": 5
            }
            
            response = requests.post(
                'http://localhost:5000/recommend',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nRecommendations:")
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"{i}. {rec['assessment_name']}")
                    print(f"   {rec['assessment_url']}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    print("="*80)
    print("API TEST SUITE")
    print("="*80)
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("Run: python3 app.py\n")
    
    time.sleep(2)
    
    if test_health():
        print("\n✓ Health check passed!")
        test_recommend()
    else:
        print("\n✗ Health check failed. Is the server running?")
