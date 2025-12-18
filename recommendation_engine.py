"""
Assessment Recommendation Engine
Uses semantic similarity for matching queries to assessments
"""
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class RecommendationEngine:
    def __init__(self, assessments_path='assessments_data.json'):
        """Initialize the recommendation engine"""
        self.assessments = self.load_assessments(assessments_path)
        self.vectorizer = None
        self.assessment_vectors = None
        self.build_index()
    
    def load_assessments(self, path):
        """Load assessment data"""
        with open(path, 'r', encoding='utf-8') as f:
            assessments = json.load(f)
        print(f"Loaded {len(assessments)} assessments")
        return assessments
    
    def preprocess_text(self, text):
        """Preprocess text for better matching"""
        # Convert to lowercase
        text = text.lower()
        
        # Expand common abbreviations
        expansions = {
            'jd': 'job description',
            'qa': 'quality assurance',
            'coo': 'chief operating officer',
            'seo': 'search engine optimization',
            'sql': 'structured query language database',
            'html': 'web development markup',
            'css': 'web styling',
            'js': 'javascript programming',
        }
        
        for abbr, expansion in expansions.items():
            text = re.sub(r'\b' + abbr + r'\b', expansion, text)
        
        return text
    
    def build_index(self):
        """Build TF-IDF index for assessments"""
        # Create searchable text for each assessment
        assessment_texts = []
        for assessment in self.assessments:
            # Combine name, category, and keywords
            text = f"{assessment['name']} {assessment['category']} {assessment.get('full_text', '')}"
            text = self.preprocess_text(text)
            assessment_texts.append(text)
        
        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        self.assessment_vectors = self.vectorizer.fit_transform(assessment_texts)
        print(f"Built index with {self.assessment_vectors.shape[1]} features")
    
    def extract_requirements(self, query):
        """Extract key requirements from query"""
        query_lower = query.lower()
        
        requirements = {
            'skills': [],
            'duration_min': None,
            'duration_max': None,
            'test_types': []
        }
        
        # Extract skills
        skill_keywords = {
            'java': ['java'],
            'python': ['python'],
            'javascript': ['javascript', 'js'],
            'sql': ['sql', 'database'],
            'excel': ['excel'],
            'selenium': ['selenium'],
            'html': ['html'],
            'css': ['css'],
            'leadership': ['leadership', 'manager', 'coo', 'executive'],
            'communication': ['communication', 'interpersonal', 'english'],
            'sales': ['sales', 'selling'],
            'analytical': ['analytical', 'analyst', 'data'],
            'personality': ['personality', 'behavioral', 'behavior'],
            'cognitive': ['cognitive', 'reasoning', 'verbal', 'numerical'],
        }
        
        for skill, keywords in skill_keywords.items():
            if any(kw in query_lower for kw in keywords):
                requirements['skills'].append(skill)
        
        # Extract duration constraints
        duration_patterns = [
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:minutes?|mins?)',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if '-' in pattern:
                    requirements['duration_min'] = int(match.group(1))
                    requirements['duration_max'] = int(match.group(2))
                else:
                    duration = int(match.group(1))
                    if 'hour' in query_lower:
                        duration *= 60
                    requirements['duration_max'] = duration
                break
        
        return requirements
    
    def recommend(self, query, top_k=10):
        """Recommend assessments for a query"""
        # Preprocess query
        processed_query = self.preprocess_text(query)
        
        # Extract requirements
        requirements = self.extract_requirements(query)
        
        # Vectorize query
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.assessment_vectors)[0]
        
        # Get top candidates (more than needed)
        top_indices = np.argsort(similarities)[::-1][:top_k * 3]
        
        # Score and filter candidates
        scored_assessments = []
        for idx in top_indices:
            assessment = self.assessments[idx]
            score = similarities[idx]
            
            # Boost score based on skill matches
            for skill in requirements['skills']:
                if skill in assessment['name'].lower() or skill in assessment['category'].lower():
                    score += 0.3
            
            scored_assessments.append({
                'assessment': assessment,
                'score': score
            })
        
        # Sort by score
        scored_assessments.sort(key=lambda x: x['score'], reverse=True)
        
        # Balance test types if needed
        recommendations = self.balance_recommendations(
            scored_assessments, 
            requirements, 
            top_k
        )
        
        return recommendations[:top_k]
    
    def balance_recommendations(self, scored_assessments, requirements, top_k):
        """Balance recommendations between technical and soft skills"""
        # Check if query mentions both technical and soft skills
        has_technical = any(skill in requirements['skills'] for skill in 
                          ['java', 'python', 'javascript', 'sql', 'html', 'css', 'selenium'])
        has_soft = any(skill in requirements['skills'] for skill in 
                      ['leadership', 'communication', 'personality'])
        
        if has_technical and has_soft:
            # Try to get a balanced mix
            technical_assessments = []
            soft_assessments = []
            other_assessments = []
            
            for item in scored_assessments:
                assessment = item['assessment']
                if assessment['test_type'] == 'K' or 'programming' in assessment['category'] or 'technical' in assessment['category']:
                    technical_assessments.append(item)
                elif assessment['test_type'] == 'P' or 'personality' in assessment['category'] or 'communication' in assessment['category']:
                    soft_assessments.append(item)
                else:
                    other_assessments.append(item)
            
            # Aim for 60% technical, 40% soft if both are requested
            num_technical = min(len(technical_assessments), int(top_k * 0.6))
            num_soft = min(len(soft_assessments), int(top_k * 0.4))
            
            balanced = technical_assessments[:num_technical] + soft_assessments[:num_soft]
            balanced.extend(other_assessments[:max(0, top_k - len(balanced))])
            
            # Re-sort by score
            balanced.sort(key=lambda x: x['score'], reverse=True)
            return balanced
        
        return scored_assessments
    
    def format_recommendations(self, recommendations):
        """Format recommendations for output"""
        results = []
        for item in recommendations:
            assessment = item['assessment']
            results.append({
                'name': assessment['name'],
                'url': assessment['url'],
                'score': float(item['score'])
            })
        return results


def main():
    """Test the recommendation engine"""
    engine = RecommendationEngine()
    
    # Test queries
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams",
        "Looking for content writer with English and SEO skills",
        "Senior Data Analyst with SQL, Python and Excel expertise",
        "Entry level sales position for new graduates"
    ]
    
    print("\n" + "="*80)
    print("TESTING RECOMMENDATION ENGINE")
    print("="*80)
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        print("-" * 80)
        
        recommendations = engine.recommend(query, top_k=5)
        formatted = engine.format_recommendations(recommendations)
        
        for i, rec in enumerate(formatted, 1):
            print(f"{i}. {rec['name']} (score: {rec['score']:.3f})")
            print(f"   {rec['url']}")


if __name__ == "__main__":
    main()
