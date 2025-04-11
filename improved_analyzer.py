"""
Improved domain analyzer with more sophisticated extraction techniques
"""
import requests
import re
import time
import random
from bs4 import BeautifulSoup

class ImprovedAnalyzer:
    """
    Improved version of the domain analyzer with better extraction capabilities
    """
    
    def __init__(self):
        # Regular expressions for extracting company names
        self.company_patterns = [
            # Standard copyright patterns
            r"(?:©|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Just the copyright year and name without legal suffix
            r"(?:©|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]{3,50})",
            # Operated by patterns
            r"(?:is\s+owned\s+and\s+operated\s+by|trading\s+as|t/a|operated\s+by)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Developed by patterns
            r"(?:developed|powered)\s+by\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Footer company with All rights reserved
            r"([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))(?:\s+All\s+[Rr]ights\s+[Rr]eserved)",
            # Contact us / about us section company names
            r"(?:Contact|About)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Company with registered address
            r"([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))(?:\s+is\s+registered\s+at)",
            # Simple company name in footer (less reliable)
            r"<footer[^>]*>.*?([A-Z][a-zA-Z0-9\s\&\-'.,]{2,50}(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.)).*?</footer>"
        ]
        
        # List of patterns for finding contact page URLs
        self.contact_patterns = [
            r'<a[^>]*href="([^"]*contact[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*about\-us[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*impressum[^"]*)"[^>]*>',  # German contact pages
            r'<a[^>]*href="([^"]*kontakt[^"]*)"[^>]*>',    # German contact pages
            r'<a[^>]*href="([^"]*imprint[^"]*)"[^>]*>',    # Another term for contact info
            r'<a[^>]*href="([^"]*about[^"]*)"[^>]*>'       # About pages often have contact info
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
    
    def fetch_homepage(self, domain):
        """Try different URL variations to get the homepage content"""
        urls = [
            f"https://{domain}",
            f"http://{domain}",
            # If domain starts with www, try without it
            f"https://{domain.replace('www.', '')}" if domain.startswith('www.') else None,
            f"http://{domain.replace('www.', '')}" if domain.startswith('www.') else None,
            # If domain doesn't start with www, try with it
            f"https://www.{domain}" if not domain.startswith('www.') else None,
            f"http://www.{domain}" if not domain.startswith('www.') else None
        ]
        
        # Filter out None values
        urls = [url for url in urls if url]
        
        for url in urls:
            print(f"  Trying {url}")
            content = self.fetch_url(url)
            if content:
                print(f"  Success with {url}")
                return {'url': url, 'content': content}
        
        return None
    
    def extract_company_name(self, text):
        """Extract company name from text using patterns"""
        if not text:
            return None
        
        candidates = []
        
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    company = match.group(1).strip()
                    # Validate and clean
                    company = self.clean_company_name(company)
                    if company and len(company) >= 3 and any(c.isalpha() for c in company):
                        candidates.append(company)
                except Exception as e:
                    print(f"  Error extracting company name: {str(e)}")
                    continue
        
        # If we found multiple candidates, take the most common one
        if candidates:
            # Count occurrences
            counts = {}
            for candidate in candidates:
                counts[candidate] = counts.get(candidate, 0) + 1
            
            # Sort by count and return the most common
            sorted_candidates = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            return sorted_candidates[0][0]
        
        return None
    
    def clean_company_name(self, name):
        """Clean up extracted company name"""
        if not name:
            return None
            
        # Remove HTML tags
        name = re.sub(r'<[^>]+>', '', name)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common words that aren't part of company names
        words_to_remove = [
            'home', 'contact', 'about', 'us', 'privacy', 'policy',
            'terms', 'conditions', 'cookies', 'sitemap', 'menu'
        ]
        for word in words_to_remove:
            name = re.sub(r'\b' + word + r'\b', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace again after word removal
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove trailing punctuation
        name = name.rstrip('.,;:')
        
        return name if len(name) >= 3 else None
    
    def find_contact_url(self, base_url, content):
        """Find contact page URL from homepage content"""
        if not base_url or not content:
            return None
        
        contact_urls = []
        
        # Extract potential contact page URLs
        for pattern in self.contact_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    href = match.group(1)
                    
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
                    
                    contact_urls.append(href)
                except:
                    continue
        
        # Return first contact URL found
        # Could be improved to check multiple and select best
        if contact_urls:
            return contact_urls[0]
        
        return None
    
    def analyze_domain(self, domain):
        """Analyze a domain to extract company information"""
        print(f"Analyzing domain: {domain}")
        
        # Fetch homepage
        result = self.fetch_homepage(domain)
        
        if not result:
            print(f"  Could not fetch homepage for {domain}")
            return {
                "domain": domain,
                "status": "error",
                "company_name": None,
                "contact_url": None
            }
        
        base_url = result['url']
        content = result['content']
        
        # Extract company name
        company_name = self.extract_company_name(content)
        
        # Find contact URL
        contact_url = self.find_contact_url(base_url, content)
        
        result = {
            "domain": domain,
            "status": "analyzed",
            "company_name": company_name,
            "contact_url": contact_url
        }
        
        print(f"  Results for {domain}:")
        print(f"    Company name: {company_name}")
        print(f"    Contact URL: {contact_url}")
        
        return result
    
    def analyze_domains(self, domains):
        """Analyze multiple domains with delay between requests"""
        results = []
        
        for domain in domains:
            result = self.analyze_domain(domain)
            results.append(result)
            # Add delay between requests to be nice to servers
            time.sleep(random.uniform(1, 3))
        
        return results

# Example usage
if __name__ == "__main__":
    analyzer = ImprovedAnalyzer()
    test_domains = ["example.com", "python.org", "github.com"]
    results = analyzer.analyze_domains(test_domains)
    for result in results:
        print(f"{result['domain']}: {result['company_name']} | Contact: {result['contact_url']}")