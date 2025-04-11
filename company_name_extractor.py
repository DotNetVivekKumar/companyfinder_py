"""
Advanced company name extractor from website content
"""
import re
import requests
from bs4 import BeautifulSoup
import time
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompanyNameExtractor:
    """
    Advanced extractor for finding company names in website content,
    specializing in privacy policies, footers, and about pages
    """
    
    def __init__(self, use_language_model=False):
        """
        Initialize the extractor with configurable options
        
        Args:
            use_language_model: Whether to use NLP for advanced extraction (not implemented)
        """
        self.use_language_model = use_language_model
        
        # Comprehensive patterns for finding company names
        self.company_patterns = [
            # Standard copyright patterns
            r"(?:©|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            
            # Just copyright year and name without legal suffix
            r"(?:©|copyright|\(c\))\s*(?:20\d{2}(?:-20\d{2})?)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]{3,50})",
            
            # Legal/data controller/processor patterns
            r"(?:data\s+controller|data\s+processor|data\s+owner)\s+is\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            
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
            
            # Company with registration number
            r"(?:Company\s+Registration\s+(?:Number|No)\.?:?\s+\d+\s*[-–]\s*([A-Z][a-zA-Z0-9\s\&\-'.,]+))",
            r"([A-Z][a-zA-Z0-9\s\&\-'.,]+)(?:\s+Company\s+Registration\s+(?:Number|No)\.?:?\s+\d+)",
            
            # Company with VAT number
            r"(?:VAT\s+(?:Number|No)\.?:?\s+\d+\s*[-–]\s*([A-Z][a-zA-Z0-9\s\&\-'.,]+))",
            r"([A-Z][a-zA-Z0-9\s\&\-'.,]+)(?:\s+VAT\s+(?:Number|No)\.?:?\s+\d+)",
            
            # Simple company name in footer (less reliable)
            r"<footer[^>]*>.*?([A-Z][a-zA-Z0-9\s\&\-'.,]{2,50}(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.)).*?</footer>",
            
            # Company names in meta tags
            r'<meta\s+name=["\']author["\'][^>]*content=["\']([A-Z][a-zA-Z0-9\s\&\-\'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))["\'"][^>]*>',
            r'<meta\s+property=["\']og:site_name["\'][^>]*content=["\']([A-Z][a-zA-Z0-9\s\&\-\'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))["\'"][^>]*>',
            
            # Company name in typical about page phrases
            r"(?:was\s+founded\s+(?:in|by))\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))",
            r"(?:welcome\s+to)\s+([A-Z][a-zA-Z0-9\s\&\-'.,]+(?:Ltd|Limited|LLC|Inc|Corp|Corporation|GmbH|B\.V\.|Pty\s+Ltd|S\.A\.))"
        ]
        
        # Common phrases to remove from extracted company names
        self.cleanup_phrases = [
            "All Rights Reserved",
            "Privacy Policy",
            "Terms of Service",
            "Terms and Conditions",
            "Home",
            "About",
            "Contact",
            "Copyright",
            "Website",
        ]
        
        # Patterns for finding privacy policy URLs
        self.privacy_policy_patterns = [
            r'<a[^>]*href="([^"]*privacy[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*policy[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*terms[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*imprint[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*impressum[^"]*)"[^>]*>',
            r'<a[^>]*href="([^"]*legal[^"]*)"[^>]*>'
        ]
    
    def fetch_url(self, url, max_retries=3, timeout=10):
        """
        Fetch content from a URL with error handling and retries
        
        Args:
            url: The URL to fetch
            max_retries: Number of retry attempts
            timeout: Timeout in seconds
            
        Returns:
            HTML content or None if failed
        """
        # User agent to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt+1}/{max_retries})")
                response = requests.get(url, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}")
                    return None
                elif response.status_code == 404:
                    logger.warning(f"Page not found (404) for {url}")
                    return None
                else:
                    logger.warning(f"Failed to fetch {url} - Status code: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error for {url}")
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout error for {url}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching {url}: {str(e)}")
            
            # Add delay before retry
            time.sleep(random.uniform(1, 3))
        
        return None
    
    def normalize_url(self, base_url, relative_url):
        """
        Convert a relative URL to an absolute URL
        
        Args:
            base_url: The base URL of the website
            relative_url: The relative URL to normalize
            
        Returns:
            Absolute URL
        """
        if relative_url.startswith(('http://', 'https://')):
            return relative_url
        
        # Split base URL, removing query string and fragments
        base_parts = base_url.split('#')[0].split('?')[0]
        
        if relative_url.startswith('/'):
            # Remove trailing slash from base if present
            if base_parts.endswith('/'):
                base_parts = base_parts[:-1]
            return base_parts + relative_url
        else:
            # Ensure base ends with slash
            if not base_parts.endswith('/'):
                base_parts += '/'
            return base_parts + relative_url
    
    def find_privacy_policy_url(self, base_url, homepage_content):
        """
        Find URLs for privacy policy or terms pages
        
        Args:
            base_url: Base URL of the website
            homepage_content: HTML content of the homepage
            
        Returns:
            List of discovered privacy policy URLs
        """
        policy_urls = []
        
        # Extract potential policy URLs using regex patterns
        for pattern in self.privacy_policy_patterns:
            matches = re.finditer(pattern, homepage_content, re.IGNORECASE)
            for match in matches:
                try:
                    href = match.group(1)
                    # Normalize URL
                    url = self.normalize_url(base_url, href)
                    policy_urls.append(url)
                except:
                    continue
        
        # Also check common paths
        common_policy_paths = [
            '/privacy',
            '/privacy-policy',
            '/terms',
            '/terms-of-service',
            '/terms-and-conditions',
            '/legal',
            '/imprint',
            '/impressum',
            '/datenschutz'
        ]
        
        for path in common_policy_paths:
            url = self.normalize_url(base_url, path)
            if url not in policy_urls:
                policy_urls.append(url)
        
        return policy_urls
    
    def extract_text_from_html(self, html_content):
        """
        Extract readable text from HTML content
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Extracted plain text
        """
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'head', 'nav']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator=' ')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_company_name_from_text(self, text):
        """
        Extract company name from plain text using regex patterns
        
        Args:
            text: Plain text to analyze
            
        Returns:
            Extracted company name or None
        """
        if not text:
            return None
        
        candidates = []
        
        # Try each pattern to find company names
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    company = match.group(1).strip()
                    # Validate with basic rules
                    if self._validate_company_name(company):
                        candidates.append(company)
                except:
                    continue
        
        # Consider frequency of mentions
        if candidates:
            counts = {}
            for candidate in candidates:
                # Normalize candidate for counting
                norm_candidate = self._normalize_company_name(candidate)
                counts[norm_candidate] = counts.get(norm_candidate, 0) + 1
            
            # Get most frequently mentioned company name
            sorted_candidates = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            best_candidate = sorted_candidates[0][0]
            
            # Clean up the company name
            clean_name = self._clean_company_name(best_candidate)
            logger.info(f"Extracted company name: {clean_name}")
            return clean_name
        
        return None
    
    def _validate_company_name(self, name):
        """
        Basic validation for a potential company name
        
        Args:
            name: Company name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Must be at least 3 characters
        if not name or len(name) < 3:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Check for suspicious patterns indicating false positive
        suspicious = [
            "all rights reserved",
            "privacy policy",
            "terms of service",
            "cookie policy",
            "sitemap",
            "contact us",
            "about us"
        ]
        
        lower_name = name.lower()
        for pattern in suspicious:
            if pattern in lower_name and len(name) < 30:  # Short matches likely false positives
                return False
        
        return True
    
    def _normalize_company_name(self, name):
        """
        Normalize company name for comparison
        
        Args:
            name: Company name to normalize
            
        Returns:
            Normalized company name
        """
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common legal entity types for comparison
        legal_suffixes = [
            "ltd", "limited", "llc", "inc", "corp", "corporation",
            "gmbh", "b.v.", "pty ltd", "s.a.", "co."
        ]
        
        for suffix in legal_suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _clean_company_name(self, name):
        """
        Clean up extracted company name
        
        Args:
            name: Raw company name
            
        Returns:
            Cleaned company name
        """
        if not name:
            return None
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', '', name)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove common phrases that aren't part of company names
        for phrase in self.cleanup_phrases:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            cleaned = pattern.sub('', cleaned)
        
        # Remove trailing punctuation
        cleaned = cleaned.rstrip('.,;:')
        
        # Remove extra whitespace again after cleanup
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def extract_company_name(self, domain):
        """
        Main method to extract company name from a domain
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with domain, status and company name
        """
        logger.info(f"Extracting company name for domain: {domain}")
        
        result = {
            "domain": domain,
            "status": "pending",
            "company_name": None
        }
        
        # Try different URL formats
        urls = [
            f"https://{domain}",
            f"http://{domain}",
            f"https://www.{domain}" if not domain.startswith('www.') else None,
            f"http://www.{domain}" if not domain.startswith('www.') else None
        ]
        
        # Filter out None values
        urls = [url for url in urls if url]
        
        # Try to fetch homepage
        homepage_url = None
        homepage_content = None
        
        for url in urls:
            content = self.fetch_url(url)
            if content:
                homepage_url = url
                homepage_content = content
                break
        
        if not homepage_url or not homepage_content:
            logger.warning(f"Could not access domain: {domain}")
            result["status"] = "error"
            return result
        
        # First try to find company name in homepage
        company_name = self.extract_company_name_from_text(homepage_content)
        
        # If found on homepage, return it
        if company_name:
            result["status"] = "analyzed"
            result["company_name"] = company_name
            return result
        
        # Otherwise, try to find privacy policy or terms pages
        policy_urls = self.find_privacy_policy_url(homepage_url, homepage_content)
        
        # Check each policy URL
        for url in policy_urls:
            logger.info(f"Checking policy URL: {url}")
            content = self.fetch_url(url)
            
            if content:
                # First try with HTML content (for patterns targeting HTML structure)
                company_name = self.extract_company_name_from_text(content)
                
                # If not found, try with plain text
                if not company_name:
                    text = self.extract_text_from_html(content)
                    company_name = self.extract_company_name_from_text(text)
                
                if company_name:
                    result["status"] = "analyzed"
                    result["company_name"] = company_name
                    return result
        
        # If no company name found in any source
        result["status"] = "analyzed"
        return result

# Example usage
if __name__ == "__main__":
    extractor = CompanyNameExtractor()
    test_domains = ["example.com", "python.org", "github.com"]
    
    for domain in test_domains:
        result = extractor.extract_company_name(domain)
        print(f"Domain: {domain}")
        print(f"Status: {result['status']}")
        print(f"Company name: {result['company_name']}")
        print("-------------------")
        # Be nice to servers with a delay
        time.sleep(random.uniform(2, 5))