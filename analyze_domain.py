import requests
import sys
import json

def analyze_domain(domain):
    """Analyze a domain using the API"""
    # Use localhost if running locally
    url = f"http://localhost:5000/api/analyze/{domain}"
    try:
        print(f"Analyzing domain: {domain}")
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"Domain: {result.get('domain')}")
            print(f"Status: {result.get('status')}")
            print(f"Company name: {result.get('company_name')}")
            print(f"Contact URL: {result.get('contact_url')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = "example.com"
    analyze_domain(domain)