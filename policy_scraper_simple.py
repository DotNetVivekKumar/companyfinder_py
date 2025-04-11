"""
Simple policy scraper for extracting company information from privacy policies
"""
import requests
import re
import time
import random
from bs4 import BeautifulSoup

class PolicyScraperSimple:
    """
    A simplified policy scraper that extracts company information 
    from privacy policies and terms of service pages
    """
    
    def __init__(self):
        # Common paths for privacy policies and terms
        self.policy_paths = [
            "/privacy",
            "/privacy-policy",
            "/privacy-notice",
            "/privacypolicy",
            "/terms",
            "/terms-of-service",
            "/terms-and-conditions",
            "/legal",
            "/data-protection",
            "/datenschutz",  # German privacy policy
            "/impressum"      # German imprint
        ]
        
        # Patterns for company identifiers
        self.company_patterns = [
            # Standard legal entity patterns
            r"([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Data controller patterns
            r"data\s+controller\s+is\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Operated by patterns
            r"operated\s+by\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Copyright owner patterns
            r"(?:©|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))"
        ]
    
    def fetch_url(self, url, timeout=10):
        """Fetch content from a URL with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"  Error fetching {url}: {str(e)}")
            return None
    
    def get_base_url(self, domain):
        """Get the base URL for a domain by testing https and http"""
        urls = [
            f"https://{domain}",
            f"http://{domain}",
            f"https://www.{domain}" if not domain.startswith('www.') else None,
            f"http://www.{domain}" if not domain.startswith('www.') else None
        ]
        
        # Filter out None values
        urls = [url for url in urls if url]
        
        for url in urls:
            content = self.fetch_url(url)
            if content:
                return url
        
        return None
    
    def find_policy_urls(self, base_url, homepage_content):
        """Find URLs for privacy policies and terms pages"""
        if not base_url or not homepage_content:
            return []
        
        policy_urls = []
        
        # First try to find links in the homepage
        soup = BeautifulSoup(homepage_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text().lower()
            
            # Check if link text contains privacy/terms keywords
            if any(keyword in link_text for keyword in ['privacy', 'privat', 'terms', 'legal', 'imprint']):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    # Remove any fragment or query
                    base = base_url.split('#')[0].split('?')[0]
                    if base.endswith('/'):
                        href = base + href[1:]
                    else:
                        href = base + href
                elif not href.startswith(('http://', 'https://')):
                    if base_url.endswith('/'):
                        href = base_url + href
                    else:
                        href = base_url + '/' + href
                
                policy_urls.append(href)
        
        # Then try common paths
        for path in self.policy_paths:
            if base_url.endswith('/'):
                policy_url = base_url + path[1:]
            else:
                policy_url = base_url + path
            
            # Don't add duplicates
            if policy_url not in policy_urls:
                policy_urls.append(policy_url)
        
        return policy_urls
    
    def extract_text_from_html(self, html):
        """Extract readable text from HTML"""
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_company_name(self, text):
        """Extract company name from policy text"""
        if not text:
            return None
        
        candidates = []
        
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    company = match.group(1).strip()
                    # Basic validation
                    if len(company) >= 3 and any(c.isalpha() for c in company):
                        candidates.append(company)
                except:
                    continue
        
        # Count occurrences and return most common
        if candidates:
            counts = {}
            for candidate in candidates:
                counts[candidate] = counts.get(candidate, 0) + 1
            
            sorted_candidates = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            return sorted_candidates[0][0]
        
        return None
    
    def scrape_domain(self, domain):
        """Scrape a domain to find company information from policies"""
        print(f"Scraping policies for domain: {domain}")
        
        # Get base URL
        base_url = self.get_base_url(domain)
        if not base_url:
            print(f"  Could not access domain: {domain}")
            return {
                "domain": domain,
                "status": "error",
                "company_name": None
            }
        
        # Get homepage content
        homepage_content = self.fetch_url(base_url)
        
        # Find policy URLs
        policy_urls = self.find_policy_urls(base_url, homepage_content)
        
        if not policy_urls:
            print(f"  Could not find any policy URLs for {domain}")
            # Try company name extraction from homepage as fallback
            company_name = self.extract_company_name(self.extract_text_from_html(homepage_content))
            return {
                "domain": domain,
                "status": "analyzed",
                "company_name": company_name
            }
        
        # Try each policy URL to find company information
        for url in policy_urls:
            print(f"  Checking policy URL: {url}")
            content = self.fetch_url(url)
            if content:
                # Extract text
                text = self.extract_text_from_html(content)
                
                # Extract company name
                company_name = self.extract_company_name(text)
                
                if company_name:
                    print(f"  Found company name in {url}: {company_name}")
                    return {
                        "domain": domain,
                        "status": "analyzed",
                        "company_name": company_name
                    }
        
        # If we get here, we couldn't find a company name in any policy
        print(f"  Could not find company name in any policy for {domain}")
        return {
            "domain": domain,
            "status": "analyzed",
            "company_name": None
        }

# Example usage
if __name__ == "__main__":
    scraper = PolicyScraperSimple()
    test_domains = ["example.com", "python.org", "github.com"]
    
    for domain in test_domains:
        result = scraper.scrape_domain(domain)
        print(f"{domain}: {result['company_name']}")
        # Add delay between requests
        time.sleep(random.uniform(1, 3))