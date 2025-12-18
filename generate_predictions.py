"""
Generate predictions on the test set
"""
import pandas as pd
from recommendation_engine import RecommendationEngine
import sys

def generate_predictions(excel_path, output_csv='test_predictions.csv'):
    """Generate predictions for test queries"""
    
    # Initialize engine
    print("Initializing recommendation engine...")
    engine = RecommendationEngine('assessments_data.json')
    
    # Load test data
    print(f"\nLoading test data from: {excel_path}")
    df_test = pd.read_excel(excel_path, sheet_name='Test-Set')
    print(f"Found {len(df_test)} test queries")
    
    # Generate predictions
    predictions = []
    
    for idx, row in df_test.iterrows():
        query = row['Query']
        print(f"\n[{idx+1}/{len(df_test)}] Processing query...")
        print(f"Query: {query[:80]}...")
        
        # Get top 10 recommendations
        recommendations = engine.recommend(query, top_k=10)
        formatted = engine.format_recommendations(recommendations)
        
        # Add each recommendation to predictions
        for rec in formatted:
            predictions.append({
                'Query': query,
                'Assessment_url': rec['url']
            })
        
        print(f"  → Generated {len(formatted)} recommendations")
    
    # Create DataFrame
    df_predictions = pd.DataFrame(predictions)
    
    # Save to CSV
    df_predictions.to_csv(output_csv, index=False)
    print(f"\n✓ Saved predictions to {output_csv}")
    print(f"  Total rows: {len(df_predictions)}")
    
    # Show sample
    print("\nSample predictions:")
    print(df_predictions.head(10))
    
    return df_predictions

def main():
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = 'Gen_AI Dataset.xlsx'  # Now in project folder
    
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]
    else:
        output_csv = 'test_predictions.csv'
    
    generate_predictions(excel_path, output_csv)

if __name__ == "__main__":
    main()
