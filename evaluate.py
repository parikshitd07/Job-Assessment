"""
Evaluate the recommendation system using Mean Recall@K
"""
import pandas as pd
import numpy as np

def calculate_recall_at_k(predictions, ground_truth, k=10):
    """
    Calculate Recall@K for each query
    
    Recall@K = (Number of relevant items in top K) / (Total relevant items)
    """
    recalls = []
    
    for query in ground_truth['Query'].unique():
        # Get ground truth URLs for this query
        relevant_urls = set(ground_truth[ground_truth['Query'] == query]['Assessment_url'].values)
        
        # Get predicted URLs for this query (top K)
        predicted_urls = set(predictions[predictions['Query'] == query]['Assessment_url'].head(k).values)
        
        # Calculate recall
        if len(relevant_urls) > 0:
            num_relevant_in_topk = len(relevant_urls.intersection(predicted_urls))
            recall = num_relevant_in_topk / len(relevant_urls)
            recalls.append(recall)
            
            print(f"Query: {query[:60]}...")
            print(f"  Relevant items: {len(relevant_urls)}")
            print(f"  Found in top-{k}: {num_relevant_in_topk}")
            print(f"  Recall@{k}: {recall:.3f}\n")
    
    mean_recall = np.mean(recalls) if recalls else 0
    return mean_recall, recalls

def evaluate_on_training_data(excel_path='Gen_AI Dataset.xlsx'):
    """Evaluate on training data"""
    print("="*80)
    print("EVALUATION ON TRAINING DATA")
    print("="*80)
    
    # Load training data as ground truth
    df_train = pd.read_excel(excel_path, sheet_name='Train-Set')
    
    # Load predictions (we'll generate them)
    from recommendation_engine import RecommendationEngine
    
    engine = RecommendationEngine('assessments_data.json')
    
    predictions = []
    for query in df_train['Query'].unique():
        recommendations = engine.recommend(query, top_k=10)
        formatted = engine.format_recommendations(recommendations)
        for rec in formatted:
            predictions.append({
                'Query': query,
                'Assessment_url': rec['url']
            })
    
    df_predictions = pd.DataFrame(predictions)
    
    # Calculate metrics
    print("\nCalculating Recall@10...\n")
    mean_recall_10, recalls_10 = calculate_recall_at_k(df_predictions, df_train, k=10)
    
    print("="*80)
    print(f"MEAN RECALL@10: {mean_recall_10:.4f}")
    print("="*80)
    
    print(f"\nRecall distribution:")
    print(f"  Min: {min(recalls_10):.4f}")
    print(f"  Max: {max(recalls_10):.4f}")
    print(f"  Median: {np.median(recalls_10):.4f}")
    print(f"  Std: {np.std(recalls_10):.4f}")
    
    return mean_recall_10

def main():
    import sys
    
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = 'Gen_AI Dataset.xlsx'  # Now in project folder
    
    evaluate_on_training_data(excel_path)

if __name__ == "__main__":
    main()
