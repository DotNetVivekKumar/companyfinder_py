import os
import json
import sys
from datetime import datetime

# Initial mock data
INITIAL_DOMAINS = [
    {"domain": "ettaloves.com", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:00:00"},
    {"domain": "weblegs.co.uk", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:05:00"},
    {"domain": "www.just-keepers.com", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:10:00"},
    {"domain": "www.racketworld.co.uk", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:15:00"}
]

def reset_db(db_file="domains_db.json", verbose=True):
    """Reset the database file to initial state"""
    try:
        if verbose:
            print(f"Resetting database {db_file} to initial state...")
        
        # Write initial data
        with open(db_file, 'w') as f:
            json.dump(INITIAL_DOMAINS, f, indent=2)
        
        if verbose:
            print(f"Successfully reset database with {len(INITIAL_DOMAINS)} domains")
        
        # Verify the data was written
        with open(db_file, 'r') as f:
            domains = json.load(f)
        
        if verbose:
            print(f"Verified database reset. Contains {len(domains)} domains:")
            for domain in domains:
                print(f"  - {domain['domain']}")
        
        return True
    except Exception as e:
        if verbose:
            print(f"Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    db_file = "domains_db.json"
    
    # Check if a different file was specified
    if len(sys.argv) > 1:
        db_file = sys.argv[1]
    
    # Reset the database
    success = reset_db(db_file)
    
    if success:
        print("Database reset successful!")
    else:
        print("Database reset failed!")