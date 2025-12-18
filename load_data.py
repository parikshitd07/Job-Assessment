"""
Load and process the training data from Excel file
"""
import pandas as pd
import json

def load_training_data(excel_path):
    """Load training data from Excel file"""
    try:
        # Read the Train-Set sheet
        df_train = pd.read_excel(excel_path, sheet_name='Train-Set')
        print(f"Loaded {len(df_train)} training examples")
        print(f"Columns: {df_train.columns.tolist()}")
        print(f"\nFirst few rows:")
        print(df_train.head())
        
        # Extract unique assessment URLs
        unique_urls = df_train['Assessment_url'].unique()
        print(f"\nFound {len(unique_urls)} unique assessment URLs in training data")
        
        return df_train, unique_urls
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def load_test_data(excel_path):
    """Load test data from Excel file"""
    try:
        # Read the Test-Set sheet
        df_test = pd.read_excel(excel_path, sheet_name='Test-Set')
        print(f"\nLoaded {len(df_test)} test queries")
        print(df_test.head())
        
        return df_test
        
    except Exception as e:
        print(f"Error loading test data: {e}")
        return None

def extract_assessment_name_from_url(url):
    """Extract assessment name from URL"""
    # URL format: https://www.shl.com/.../view/assessment-name/
    if '/view/' in url:
        parts = url.rstrip('/').split('/view/')
        if len(parts) > 1:
            name = parts[1].split('/')[0]
            # Clean up the name
            name = name.replace('-', ' ').title()
            # Remove (new) or other parenthetical content
            name = name.split('(')[0].strip()
            return name
    return "Unknown Assessment"

def main():
    """Test data loading"""
    import sys
    
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = 'Gen_AI Dataset.xlsx'
    
    print(f"Loading data from: {excel_path}")
    df_train, unique_urls = load_training_data(excel_path)
    
    if df_train is not None:
        # Group by query to see how many assessments per query
        grouped = df_train.groupby('Query')['Assessment_url'].apply(list).reset_index()
        print(f"\n\nNumber of assessments per query:")
        for idx, row in grouped.iterrows():
            print(f"\nQuery: {row['Query'][:80]}...")
            print(f"Number of assessments: {len(row['Assessment_url'])}")
        
        # Extract names
        print("\n\nSample assessment names:")
        for url in list(unique_urls)[:10]:
            name = extract_assessment_name_from_url(url)
            print(f"{name}: {url}")
    
    # Load test data
    df_test = load_test_data(excel_path)

if __name__ == "__main__":
    main()
