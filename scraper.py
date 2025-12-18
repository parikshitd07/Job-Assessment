"""
SHL Product Catalog Scraper
Crawls the SHL website to extract Individual Test Solutions
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

class SHLScraper:
    def __init__(self):
        self.base_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def get_product_listing_page(self):
        """Fetch the main product catalog page"""
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching main page: {e}")
            return None
    
    def extract_product_urls(self, html_content):
        """Extract all individual test solution URLs from the catalog"""
        soup = BeautifulSoup(html_content, 'lxml')
        product_urls = set()
        
        # Find all links that point to product catalog items
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # Match URLs that are individual product pages
            if '/product-catalog/view/' in href:
                full_url = urljoin(self.base_url, href)
                # Clean the URL (remove fragments)
                full_url = full_url.split('#')[0]
                product_urls.add(full_url)
        
        print(f"Found {len(product_urls)} unique product URLs")
        return list(product_urls)
    
    def scrape_product_details(self, url):
        """Scrape details from an individual product page"""
        try:
            time.sleep(0.5)  # Be respectful with requests
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract product details
            product_data = {
                'url': url,
                'name': '',
                'description': '',
                'test_type': '',
                'duration': '',
                'skills': [],
                'category': '',
                'full_text': ''
            }
            
            # Extract title/name
            title = soup.find('h1')
            if title:
                product_data['name'] = title.get_text(strip=True)
            
            # Extract description from various possible locations
            description_sections = []
            
            # Look for meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description_sections.append(meta_desc['content'])
            
            # Look for main content areas
            content_divs = soup.find_all(['div', 'section'], class_=re.compile('content|description|overview'))
            for div in content_divs:
                text = div.get_text(strip=True)
                if len(text) > 50:  # Only substantial text
                    description_sections.append(text)
            
            # Extract all paragraph text
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:
                    description_sections.append(text)
            
            product_data['description'] = ' '.join(description_sections)
            
            # Extract test type and other metadata
            # Look for duration information
            duration_patterns = [
                r'(\d+)\s*(?:minutes?|mins?)',
                r'(\d+)\s*(?:hours?|hrs?)',
                r'Duration[:\s]+(\d+)',
            ]
            
            full_text = soup.get_text()
            for pattern in duration_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    product_data['duration'] = match.group(0)
                    break
            
            # Extract test type (K, P, etc.)
            test_type_match = re.search(r'Test Type[:\s]+([A-Z])', full_text)
            if test_type_match:
                product_data['test_type'] = test_type_match.group(1)
            
            # Store full text for later use
            product_data['full_text'] = full_text
            
            # Extract product name from URL as fallback
            if not product_data['name']:
                url_parts = url.rstrip('/').split('/')
                if url_parts:
                    product_data['name'] = url_parts[-1].replace('-', ' ').title()
            
            return product_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_all_products(self, max_products=None):
        """Main method to scrape all products"""
        print("Starting SHL Product Catalog scraping...")
        
        # Get main page
        html = self.get_product_listing_page()
        if not html:
            print("Failed to fetch main page")
            return []
        
        # Extract product URLs
        product_urls = self.extract_product_urls(html)
        
        if max_products:
            product_urls = product_urls[:max_products]
        
        # Scrape each product
        products = []
        for i, url in enumerate(product_urls):
            print(f"Scraping product {i+1}/{len(product_urls)}: {url}")
            product_data = self.scrape_product_details(url)
            if product_data:
                products.append(product_data)
        
        print(f"\nSuccessfully scraped {len(products)} products")
        return products
    
    def save_to_json(self, products, filename='shl_products.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(products)} products to {filename}")


def main():
    """Test the scraper"""
    scraper = SHLScraper()
    
    # First, let's test with a few products
    print("Testing scraper with 10 products...")
    products = scraper.scrape_all_products(max_products=10)
    
    if products:
        scraper.save_to_json(products, 'shl_products_test.json')
        print("\nSample product:")
        print(json.dumps(products[0], indent=2))
        print(f"\nTotal products scraped: {len(products)}")
    else:
        print("No products were scraped successfully")


if __name__ == "__main__":
    main()
