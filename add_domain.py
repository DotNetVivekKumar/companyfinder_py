import requests
import sys
import json

def add_domain(domain):
    """Add a domain to the API"""
    # Use localhost if running locally
    url = "http://localhost:5000/api/domains"
    try:
        response = requests.post(url, json={"domain": domain})
        if response.status_code == 201:
            print(f"Domain {domain} added successfully!")
        elif response.status_code == 409:
            print(f"Domain {domain} already exists!")
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
    add_domain(domain)