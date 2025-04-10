import requests
import re
import time
import random

class DomainAnalyzer:
    """
    Simple domain analyzer that extracts company information from websites
    """
    
    def __init__(self):
        # Simple regex patterns for company names
        self.company_patterns = [
            # Copyright patterns
            r"(?:\u00a9|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-']+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Just copyright year and name
            r"(?:\u00a9|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-']+)",
            # Operated by patterns
            r"(?:is\s+owned\s+and\s+operated\s+by|trading\s+as|t/a|operated\s+by)\s+([A-Z][a-zA-Z0-9\s\&\-']+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            # Footer company with All rights reserved
            r"([A-Z][a-zA-Z0-9\s\&\-']+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))(?:\s+All\s+[Rr]ights\s+[Rr]eserved)"
        ]
    
    def fetch_homepage(self, domain):
        """Fetch the homepage content of a domain"""
        try:
            # Try different URL formats
            urls = [
                f"https://{domain}",
                f"http://{domain}",
                f"https://www.{domain}" if not domain.startswith('www.') else None,
                f"http://www.{domain}" if not domain.startswith('www.') else None
            ]
            
            # Filter out None values
            urls = [url for url in urls if url]
            
            for url in urls:
                try:
                    print(f"  Trying {url}")
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"  Success with {url}")
                        return response.text
                except Exception as e:
                    print(f"  Error with {url}: {str(e)}")
                    continue
            
            return None
        except Exception as e:
            print(f"Error fetching {domain}: {str(e)}")
            return None
    
    def extract_company_name(self, text):
        """Extract company name from text using simple patterns"""
        if not text:
            return None
        
        candidates = []
        
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    company = match.group(1).strip()
                    # Validate: Must be at least 3 chars and contain a letter
                    if len(company) >= 3 and any(c.isalpha() for c in company):
                        candidates.append(company)
                except:
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
    
    def analyze_domain(self, domain):
        """Analyze a single domain and extract company name"""
        print(f"Analyzing domain: {domain}")
        
        # Fetch homepage
        content = self.fetch_homepage(domain)
        
        if not content:
            print(f"  Could not fetch homepage for {domain}")
            return {
                "domain": domain,
                "status": "error",
                "company_name": None
            }
        
        # Extract company name
        company_name = self.extract_company_name(content)
        
        result = {
            "domain": domain,
            "status": "analyzed",
            "company_name": company_name
        }
        
        print(f"  Results for {domain}: Company name: {company_name}")
        return result
    
    def analyze_domains(self, domains):
        """Analyze multiple domains and compile results"""
        results = []
        
        for domain in domains:
            result = self.analyze_domain(domain)
            results.append(result)
            # Be nice to servers - add a random delay
            time.sleep(random.uniform(1, 3))
        
        return results

# Example usage
if __name__ == "__main__":
    analyzer = DomainAnalyzer()
    test_domains = ["example.com", "python.org", "github.com"]
    results = analyzer.analyze_domains(test_domains)
    for result in results:
        print(f"{result['domain']}: {result['company_name']}")