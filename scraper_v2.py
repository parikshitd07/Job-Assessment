"""
Targeted SHL Assessment Scraper
Scrapes only the URLs from training data to build initial dataset
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import pandas as pd

class TargetedSHLScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_product_details(self, url):
        """Scrape details from an individual product page"""
        try:
            print(f"Scraping: {url}")
            time.sleep(0.3)  # Be respectful
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract product details
            product_data = {
                'url': url,
                'name': '',
                'description': '',
                'test_type': '',
                'duration': '',
                'category': '',
                'skills': [],
                'full_text': ''
            }
            
            # Extract title/name
            title = soup.find('h1')
            if title:
                product_data['name'] = title.get_text(strip=True)
            
            # Fallback: extract name from URL
            if not product_data['name']:
                url_parts = url.rstrip('/').split('/view/')
                if len(url_parts) > 1:
                    name = url_parts[1].split('/')[0]
                    product_data['name'] = name.replace('-', ' ').title()
            
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                product_data['description'] = meta_desc['content']
            
            # Get all text content
            full_text = soup.get_text(separator=' ', strip=True)
            product_data['full_text'] = full_text
            
            # Extract duration
            duration_patterns = [
                r'(\d+)\s*(?:minutes?|mins?)',
                r'(\d+)\s*(?:hours?|hrs?)',
                r'(\d+\s*-\s*\d+)\s*(?:minutes?|mins?)',
            ]
            
            for pattern in duration_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    product_data['duration'] = match.group(0)
                    break
            
            # Extract test type
            test_type_match = re.search(r'Test\s+Type[:\s]+([A-Z])', full_text, re.IGNORECASE)
            if test_type_match:
                product_data['test_type'] = test_type_match.group(1)
            
            # Extract category keywords
            categories = []
            category_keywords = {
                'programming': ['java', 'python', 'javascript', 'programming', 'coding', 'software', 'developer'],
                'personality': ['personality', 'behavior', 'opq', 'behavioral'],
                'cognitive': ['cognitive', 'verbal', 'numerical', 'reasoning', 'inductive'],
                'sales': ['sales', 'selling', 'customer'],
                'leadership': ['leadership', 'manager', 'executive', 'coo'],
                'communication': ['communication', 'english', 'writing', 'interpersonal'],
                'technical': ['technical', 'sql', 'database', 'selenium', 'html', 'css'],
                'administrative': ['administrative', 'admin', 'clerical']
            }
            
            text_lower = full_text.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in text_lower or keyword in product_data['name'].lower() for keyword in keywords):
                    categories.append(category)
            
            product_data['category'] = ', '.join(categories) if categories else 'general'
            
            return product_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_from_training_data(self, excel_path):
        """Scrape all URLs from training data"""
        # Load training data
        df_train = pd.read_excel(excel_path, sheet_name='Train-Set')
        unique_urls = df_train['Assessment_url'].unique()
        
        print(f"Found {len(unique_urls)} unique URLs to scrape")
        
        products = []
        for i, url in enumerate(unique_urls):
            print(f"\n[{i+1}/{len(unique_urls)}]")
            product_data = self.scrape_product_details(url)
            if product_data:
                products.append(product_data)
                print(f"✓ Scraped: {product_data['name']}")
            else:
                print(f"✗ Failed to scrape")
        
        print(f"\n\nSuccessfully scraped {len(products)} products")
        return products
    
    def save_to_json(self, products, filename='assessments_data.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(products)} products to {filename}")


def main():
    """Test the scraper"""
    scraper = TargetedSHLScraper()
    
    excel_path = 'Gen_AI Dataset.xlsx'
    print(f"Scraping URLs from training data: {excel_path}\n")
    
    products = scraper.scrape_from_training_data(excel_path)
    
    if products:
        scraper.save_to_json(products, 'assessments_data.json')
        print("\n" + "="*50)
        print("Sample product:")
        print(json.dumps(products[0], indent=2))
    else:
        print("No products were scraped successfully")


if __name__ == "__main__":
    main()
