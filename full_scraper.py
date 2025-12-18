"""
Complete SHL Catalog Scraper - Scrapes ALL Individual Test Solutions
Must get 377+ assessments as per assignment requirements
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

class FullSHLScraper:
    def __init__(self):
        self.base_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.all_product_urls = set()
    
    def get_all_catalog_pages(self):
        """Get all product URLs from the catalog"""
        print("Fetching product catalog...")
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find all product links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if '/product-catalog/view/' in href:
                    # Skip pre-packaged solutions as per requirements
                    if 'solution' not in href.lower() or 'individual' in href.lower():
                        full_url = urljoin(self.base_url, href)
                        full_url = full_url.split('#')[0].split('?')[0]  # Clean URL
                        self.all_product_urls.add(full_url)
            
            print(f"Found {len(self.all_product_urls)} product URLs")
            return list(self.all_product_urls)
            
        except Exception as e:
            print(f"Error fetching catalog: {e}")
            return []
    
    def scrape_assessment_detail(self, url):
        """Scrape detailed information from an assessment page"""
        try:
            time.sleep(0.2)  # Rate limiting
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            assessment = {
                'url': url,
                'name': '',
                'description': '',
                'test_type': '',
                'duration': 0,
                'adaptive_support': '',
                'remote_support': '',
                'categories': []
            }
            
            # Extract name
            title = soup.find('h1')
            if title:
                assessment['name'] = title.get_text(strip=True)
            else:
                # Fallback: extract from URL
                url_name = url.rstrip('/').split('/view/')[-1].replace('-', ' ').title()
                assessment['name'] = url_name
            
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                assessment['description'] = meta_desc['content']
            
            # Get all text for further extraction
            full_text = soup.get_text(separator=' ', strip=True)
            
            # Extract duration
            duration_patterns = [
                r'(\d+)\s*(?:minutes?|mins?)',
                r'(\d+)\s*(?:hours?|hrs?)',
            ]
            for pattern in duration_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    duration_val = int(match.group(1))
                    if 'hour' in match.group(0).lower():
                        duration_val *= 60
                    assessment['duration'] = duration_val
                    break
            
            # Extract test type
            test_type_match = re.search(r'Test\s+Type[:\s]+([A-Z])', full_text, re.IGNORECASE)
            if test_type_match:
                assessment['test_type'] = test_type_match.group(1)
            
            # Check for adaptive support
            if re.search(r'adaptive', full_text, re.IGNORECASE):
                assessment['adaptive_support'] = 'Yes'
            else:
                assessment['adaptive_support'] = 'No'
            
            # Check for remote support
            if re.search(r'remote', full_text, re.IGNORECASE):
                assessment['remote_support'] = 'Yes'
            else:
                assessment['remote_support'] = 'No'
            
            # Categorize based on content
            categories = []
            category_keywords = {
                'Knowledge & Skills': ['programming', 'java', 'python', 'javascript', 'sql', 'technical', 'coding', 'software'],
                'Personality & Behavior': ['personality', 'behavioral', 'opq', 'behavior'],
                'Cognitive': ['cognitive', 'verbal', 'numerical', 'reasoning', 'inductive', 'deductive'],
                'Communication': ['communication', 'english', 'writing', 'language'],
                'Sales': ['sales', 'selling', 'customer'],
                'Leadership': ['leadership', 'manager', 'management', 'executive'],
                'Administrative': ['administrative', 'admin', 'clerical']
            }
            
            text_lower = full_text.lower() + ' ' + assessment['name'].lower()
            for category, keywords in category_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    categories.append(category)
            
            assessment['categories'] = categories if categories else ['General']
            
            # Full text for embeddings/search
            assessment['full_text'] = full_text[:5000]  # Limit size
            
            return assessment
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)[:100]}")
            return None
    
    def scrape_all_parallel(self, max_workers=5):
        """Scrape all assessments in parallel"""
        urls = self.get_all_catalog_pages()
        
        if len(urls) < 100:  # Too few URLs, try alternative approach
            print("Warning: Found fewer than 100 URLs. Expanding search...")
            # Add common assessment patterns
            urls = self.expand_url_list(urls)
        
        assessments = []
        
        print(f"\nScraping {len(urls)} assessments...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_assessment_detail, url): url for url in urls}
            
            for i, future in enumerate(as_completed(future_to_url)):
                url = future_to_url[future]
                try:
                    assessment = future.result()
                    if assessment:
                        assessments.append(assessment)
                        print(f"[{i+1}/{len(urls)}] ✓ {assessment['name']}")
                    else:
                        print(f"[{i+1}/{len(urls)}] ✗ Failed")
                except Exception as e:
                    print(f"[{i+1}/{len(urls)}] ✗ Error: {str(e)[:50]}")
        
        print(f"\n✓ Successfully scraped {len(assessments)} assessments")
        return assessments
    
    def expand_url_list(self, initial_urls):
        """Expand URL list by exploring pagination and categories"""
        expanded = set(initial_urls)
        
        # Try to find more URLs through site exploration
        try:
            # Check for pagination
            for page_num in range(1, 20):
                page_url = f"{self.base_url}?page={page_num}"
                response = self.session.get(page_url, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')
                links = soup.find_all('a', href=True)
                for link in links:
                    if '/product-catalog/view/' in link['href']:
                        full_url = urljoin(self.base_url, link['href'])
                        expanded.add(full_url.split('#')[0].split('?')[0])
        except:
            pass
        
        return list(expanded)
    
    def save_to_json(self, assessments, filename='shl_full_catalog.json'):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(assessments, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to {filename}")


def main():
    """Main scraping function"""
    scraper = FullSHLScraper()
    
    print("="*80)
    print("FULL SHL CATALOG SCRAPER")
    print("="*80)
    print("\nTarget: 377+ Individual Test Solutions")
    print("This may take 10-15 minutes...\n")
    
    assessments = scraper.scrape_all_parallel(max_workers=10)
    
    print("\n" + "="*80)
    print(f"SCRAPING COMPLETE: {len(assessments)} assessments")
    print("="*80)
    
    if len(assessments) >= 377:
        print(f"✓ SUCCESS: Met requirement of 377+ assessments")
    else:
        print(f"⚠ WARNING: Only scraped {len(assessments)} assessments (need 377+)")
    
    scraper.save_to_json(assessments, 'shl_full_catalog.json')
    
    # Show sample
    if assessments:
        print("\nSample assessment:")
        print(json.dumps(assessments[0], indent=2))


if __name__ == "__main__":
    main()
