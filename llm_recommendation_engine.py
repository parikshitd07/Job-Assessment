"""
LLM-Based Assessment Recommendation Engine
Uses Google Gemini API + Sentence Transformers for hybrid retrieval
CRITICAL: This addresses the LLM integration requirement
"""
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import os
import re

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

# Try to import sentence transformers, fallback to TF-IDF
try:
    from sentence_transformers import SentenceTransformer
    USE_EMBEDDINGS = True
except (ImportError, AttributeError) as e:
    # Handle both missing package and compatibility issues
    from sklearn.feature_extraction.text import TfidfVectorizer
    USE_EMBEDDINGS = False
    print(f"⚠ Sentence-transformers not available ({str(e)[:50]}), using TF-IDF fallback")

class LLMRecommendationEngine:
    """
    Hybrid Recommendation Engine:
    1. Uses embeddings/TF-IDF for initial retrieval
    2. Uses Gemini LLM for query understanding and re-ranking
    3. Balances recommendations based on test types
    """
    
    def __init__(self, assessments_path='shl_full_catalog.json', api_key=None):
        """Initialize with LLM and embedding models"""
        self.assessments = self.load_assessments(assessments_path)
        
        # Configure Gemini API (New SDK)
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-3-flash-preview'
            # Set request timeout to 120 seconds (2 minutes)
            self.request_options = {'timeout': 120}
            self.use_llm = True
            print("✓ Gemini 3 Flash Preview API initialized (New SDK, 2 min timeout)")
        except Exception as e:
            self.client = None
            self.model_name = None
            self.use_llm = False
            self.request_options = {}
            print(f"⚠ Gemini API not available: {str(e)[:30]}, using fallback")
        
        # Initialize embedding model or TF-IDF
        if USE_EMBEDDINGS:
            print("Loading sentence-transformers model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.assessment_embeddings = None
            self.build_embedding_index()
        else:
            print("Using TF-IDF vectorizer...")
            self.vectorizer = None
            self.assessment_vectors = None
            self.build_tfidf_index()
    
    def load_assessments(self, path):
        """Load assessment catalog"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                assessments = json.load(f)
            print(f"✓ Loaded {len(assessments)} assessments from {path}")
            return assessments
        except FileNotFoundError:
            # Fallback to smaller dataset if full catalog not available yet
            try:
                with open('assessments_data.json', 'r', encoding='utf-8') as f:
                    assessments = json.load(f)
                print(f"⚠ Using fallback dataset: {len(assessments)} assessments")
                return assessments
            except:
                print("ERROR: No assessment data found!")
                return []
    
    def build_embedding_index(self):
        """Build embedding index for semantic search"""
        print("Building embedding index...")
        texts = []
        for assessment in self.assessments:
            # Combine relevant fields for embedding
            text = f"{assessment.get('name', '')} {assessment.get('description', '')} "
            text += f"{' '.join(assessment.get('categories', []))} {assessment.get('test_type', '')}"
            texts.append(text)
        
        self.assessment_embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        print(f"✓ Built embedding index with {len(self.assessment_embeddings)} vectors")
    
    def build_tfidf_index(self):
        """Fallback: Build TF-IDF index"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        texts = []
        for assessment in self.assessments:
            text = f"{assessment.get('name', '')} {assessment.get('description', '')} "
            text += f"{' '.join(assessment.get('categories', []))}"
            texts.append(text)
        
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        self.assessment_vectors = self.vectorizer.fit_transform(texts)
        print(f"✓ Built TF-IDF index")
    
    def extract_requirements_with_llm(self, query):
        """Use LLM to understand query and extract requirements"""
        if not self.use_llm:
            return self.extract_requirements_fallback(query)
        
        try:
            prompt = f"""Analyze this job requirement or query and extract key information:

Query: {query}

Extract and return in JSON format:
1. skills: List of technical skills mentioned (e.g., Java, Python, SQL)
2. soft_skills: List of soft skills (e.g., communication, leadership)
3. experience_level: entry/mid/senior level
4. test_types_needed: List from [Knowledge & Skills, Personality & Behavior, Cognitive, Communication]
5. key_focus: Brief summary of what to prioritize

Return ONLY valid JSON, no other text."""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group())
                print(f"✓ LLM extracted: {requirements.get('key_focus', '')}")
                return requirements
            else:
                return self.extract_requirements_fallback(query)
                
        except Exception as e:
            print(f"⚠ LLM extraction failed: {str(e)[:50]}, using fallback")
            return self.extract_requirements_fallback(query)
    
    def extract_requirements_fallback(self, query):
        """Fallback keyword-based requirement extraction"""
        query_lower = query.lower()
        
        requirements = {
            'skills': [],
            'soft_skills': [],
            'test_types_needed': [],
            'key_focus': 'general assessment'
        }
        
        # Extract skills
        skill_map = {
            'java': 'Java', 'python': 'Python', 'javascript': 'JavaScript',
            'sql': 'SQL', 'html': 'HTML', 'css': 'CSS'
        }
        for keyword, skill in skill_map.items():
            if keyword in query_lower:
                requirements['skills'].append(skill)
        
        # Soft skills
        if any(word in query_lower for word in ['communication', 'collaborate', 'interpersonal']):
            requirements['soft_skills'].append('Communication')
        if any(word in query_lower for word in ['leadership', 'manager', 'lead']):
            requirements['soft_skills'].append('Leadership')
        
        # Determine test types
        if requirements['skills']:
            requirements['test_types_needed'].append('Knowledge & Skills')
        if requirements['soft_skills'] or 'personality' in query_lower:
            requirements['test_types_needed'].append('Personality & Behavior')
        if any(word in query_lower for word in ['cognitive', 'reasoning', 'analytical']):
            requirements['test_types_needed'].append('Cognitive')
        
        return requirements
    
    def retrieve_candidates(self, query, top_k=30):
        """Retrieve candidate assessments using embeddings/TF-IDF"""
        if USE_EMBEDDINGS:
            query_embedding = self.embedding_model.encode([query])
            similarities = cosine_similarity(query_embedding, self.assessment_embeddings)[0]
        else:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.assessment_vectors)[0]
        
        # Get top candidates
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        candidates = []
        for idx in top_indices:
            candidates.append({
                'assessment': self.assessments[idx],
                'similarity_score': float(similarities[idx])
            })
        
        return candidates
    
    def rerank_with_llm(self, query, candidates, top_k=10):
        """Use LLM to re-rank candidates for better relevance"""
        if not self.use_llm or len(candidates) == 0:
            return candidates[:top_k]
        
        try:
            # Prepare candidate summary
            candidate_list = []
            for i, cand in enumerate(candidates[:20]):  # Limit for LLM context
                ass = cand['assessment']
                candidate_list.append(f"{i+1}. {ass['name']} - {', '.join(ass.get('categories', []))}")
            
            prompt = f"""Given this job requirement:
"{query}"

And these assessment options:
{chr(10).join(candidate_list)}

Rank the top {top_k} most relevant assessments by their index numbers.
Consider:
- Technical skills match
- Soft skills match
- Test type appropriateness
- Balance between knowledge and behavioral tests if both needed

Return ONLY a comma-separated list of index numbers (e.g., "3,1,5,7,2,4,8,9,6,10")"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            ranking_text = response.text.strip()
            
            # Parse ranking
            indices = [int(x.strip())-1 for x in re.findall(r'\d+', ranking_text)]
            
            # Reorder candidates based on LLM ranking
            reranked = []
            for idx in indices[:top_k]:
                if 0 <= idx < len(candidates):
                    reranked.append(candidates[idx])
            
            # Fill remaining with original order if needed
            for cand in candidates:
                if cand not in reranked and len(reranked) < top_k:
                    reranked.append(cand)
            
            print(f"✓ LLM re-ranked {len(reranked)} assessments")
            return reranked[:top_k]
            
        except Exception as e:
            print(f"⚠ LLM re-ranking failed: {str(e)[:50]}, using similarity order")
            return candidates[:top_k]
    
    def recommend(self, query, top_k=10):
        """Main recommendation function with full LLM integration"""
        print(f"\n{'='*60}")
        print(f"Query: {query[:100]}...")
        print('='*60)
        
        # Step 1: Extract requirements using LLM
        requirements = self.extract_requirements_with_llm(query)
        
        # Step 2: Retrieve candidates using embeddings
        candidates = self.retrieve_candidates(query, top_k=30)
        print(f"→ Retrieved {len(candidates)} candidates")
        
        # Step 3: Re-rank using LLM
        reranked = self.rerank_with_llm(query, candidates, top_k=top_k)
        
        # Step 4: Balance test types if needed
        final_recommendations = self.balance_by_test_type(reranked, requirements, top_k)
        
        print(f"✓ Final: {len(final_recommendations)} recommendations")
        return final_recommendations
    
    def balance_by_test_type(self, candidates, requirements, top_k):
        """Ensure balanced mix of test types"""
        test_types_needed = requirements.get('test_types_needed', [])
        
        if len(test_types_needed) < 2:
            return candidates[:top_k]
        
        # Separate by test type
        by_type = {'K': [], 'P': [], 'Other': []}
        for cand in candidates:
            test_type = cand['assessment'].get('test_type', '')
            if test_type == 'K':
                by_type['K'].append(cand)
            elif test_type == 'P':
                by_type['P'].append(cand)
            else:
                by_type['Other'].append(cand)
        
        # Mix appropriately
        balanced = []
        if 'Knowledge & Skills' in test_types_needed and 'Personality & Behavior' in test_types_needed:
            # 60-40 split
            balanced.extend(by_type['K'][:int(top_k * 0.6)])
            balanced.extend(by_type['P'][:int(top_k * 0.4)])
        else:
            balanced = candidates[:top_k]
        
        # Fill remaining
        for cand in candidates:
            if cand not in balanced and len(balanced) < top_k:
                balanced.append(cand)
        
        return balanced[:top_k]
    
    def format_for_api(self, recommendations):
        """Format recommendations for API response"""
        return [{
            'assessment_name': rec['assessment']['name'],
            'assessment_url': rec['assessment']['url'],
            'description': rec['assessment'].get('description', '')[:200],
            'duration': rec['assessment'].get('duration', 0),
            'test_type': rec['assessment'].get('test_type', ''),
            'adaptive_support': rec['assessment'].get('adaptive_support', 'No'),
            'remote_support': rec['assessment'].get('remote_support', 'No')
        } for rec in recommendations]


def main():
    """Test the LLM recommendation engine"""
    print("="*80)
    print("LLM-BASED RECOMMENDATION ENGINE TEST")
    print("="*80)
    
    # Initialize (will use Gemini if API key available)
    engine = LLMRecommendationEngine()
    
    # Test queries
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams",
        "Senior Data Analyst with SQL, Python and Excel expertise",
        "Entry level sales position for new graduates"
    ]
    
    for query in test_queries:
        recommendations = engine.recommend(query, top_k=5)
        formatted = engine.format_for_api(recommendations)
        
        print(f"\nTop 5 recommendations:")
        for i, rec in enumerate(formatted, 1):
            print(f"{i}. {rec['assessment_name']}")
            print(f"   {rec['assessment_url']}")
        print()


if __name__ == "__main__":
    main()
