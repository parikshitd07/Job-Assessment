"""
Create mock assessment data from training URLs for initial testing
"""
import pandas as pd
import json

def create_mock_assessments():
    """Create mock assessment data from training data URLs"""
    excel_path = 'Gen_AI Dataset.xlsx'
    df_train = pd.read_excel(excel_path, sheet_name='Train-Set')
    
    # Get unique URLs
    unique_urls = df_train['Assessment_url'].unique()
    
    assessments = []
    for url in unique_urls:
        # Extract name from URL
        url_parts = url.rstrip('/').split('/view/')
        if len(url_parts) > 1:
            name = url_parts[1].split('/')[0]
            clean_name = name.replace('-', ' ').title()
        else:
            clean_name = "Assessment"
        
        # Create mock assessment with name and URL
        assessment = {
            'url': url,
            'name': clean_name,
            'description': f"Assessment for {clean_name}",
            'test_type': '',
            'duration': '',
            'category': '',
            'full_text': f"{clean_name} assessment"
        }
        
        # Add keywords based on name
        name_lower = clean_name.lower()
        
        # Infer categories from name
        categories = []
        if any(word in name_lower for word in ['java', 'python', 'javascript', 'programming', 'coding']):
            categories.append('programming')
            assessment['test_type'] = 'K'
        if any(word in name_lower for word in ['personality', 'opq', 'behavior']):
            categories.append('personality')
            assessment['test_type'] = 'P'
        if any(word in name_lower for word in ['verbal', 'numerical', 'reasoning', 'cognitive']):
            categories.append('cognitive')
            assessment['test_type'] = 'K'
        if any(word in name_lower for word in ['sales', 'selling']):
            categories.append('sales')
        if any(word in name_lower for word in ['leadership', 'manager', 'executive']):
            categories.append('leadership')
        if any(word in name_lower for word in ['communication', 'english', 'writing', 'interpersonal']):
            categories.append('communication')
        if any(word in name_lower for word in ['sql', 'database', 'selenium', 'html', 'css', 'technical']):
            categories.append('technical')
            assessment['test_type'] = 'K'
        if any(word in name_lower for word in ['admin', 'clerical']):
            categories.append('administrative')
        
        assessment['category'] = ', '.join(categories) if categories else 'general'
        
        # Enhanced full_text for better matching
        assessment['full_text'] = f"{clean_name} {' '.join(categories)} assessment test skills evaluation"
        
        assessments.append(assessment)
    
    print(f"Created {len(assessments)} mock assessments")
    
    # Save to JSON
    with open('assessments_data.json', 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    
    print("Saved to assessments_data.json")
    
    # Print sample
    print("\nSample assessments:")
    for i, assessment in enumerate(assessments[:5]):
        print(f"\n{i+1}. {assessment['name']}")
        print(f"   URL: {assessment['url']}")
        print(f"   Categories: {assessment['category']}")
    
    return assessments

if __name__ == "__main__":
    create_mock_assessments()
