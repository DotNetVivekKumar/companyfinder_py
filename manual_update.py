import requests
import sys
import json

def update_domains(domain=None):
    """Manually update domains via the API"""
    # Use localhost if running locally
    url = "http://localhost:5000/api/update-all" if domain is None else f"http://localhost:5000/api/domains/{domain}"
    
    try:
        if domain is None:
            # Update all domains
            print(f"Updating all domains...")
            response = requests.get(url)
        else:
            # Update a specific domain with test data
            print(f"Updating domain: {domain}")
            data = {
                "status": "analyzed",
                "company_name": f"Test Company for {domain}",
                "contact_url": f"https://{domain}/contact"
            }
            response = requests.put(url, json=data)
        
        # Print response
        if response.status_code == 200:
            result = response.json()
            print("Update successful!")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # If a domain is provided as an argument, update just that domain
    # Otherwise, update all domains
    if len(sys.argv) > 1:
        domain = sys.argv[1]
        update_domains(domain)
    else:
        update_domains()