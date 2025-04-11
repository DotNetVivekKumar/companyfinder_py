"""
Test script for the company name extractor
"""
import json
import time
import random
from company_name_extractor import CompanyNameExtractor

def test_extraction(domains, output_file="test_extraction_results.json"):
    """
    Test company name extraction on a list of domains and save results to a file
    
    Args:
        domains: List of domains to test
        output_file: Path to save results
    """
    extractor = CompanyNameExtractor()
    results = []
    
    print(f"Testing extraction on {len(domains)} domains")
    
    for i, domain in enumerate(domains):
        print(f"[{i+1}/{len(domains)}] Processing {domain}")
        
        try:
            # Extract company name
            result = extractor.extract_company_name(domain)
            results.append(result)
            
            # Print results
            print(f"  Status: {result['status']}")
            print(f"  Company name: {result['company_name']}")
            
            # Save progress after each domain
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Add delay between requests to be nice to servers
            delay = random.uniform(1, 3)
            print(f"  Waiting {delay:.2f} seconds before next domain...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"  Error processing {domain}: {str(e)}")
            # Add failed result
            results.append({
                "domain": domain,
                "status": "error",
                "company_name": None,
                "error": str(e)
            })
    
    # Calculate success rate
    success_count = sum(1 for r in results if r["status"] == "analyzed" and r["company_name"])
    error_count = sum(1 for r in results if r["status"] == "error")
    not_found_count = sum(1 for r in results if r["status"] == "analyzed" and not r["company_name"])
    
    print("\nExtraction results summary:")
    print(f"Total domains: {len(domains)}")
    print(f"Successful extractions: {success_count} ({success_count/len(domains)*100:.1f}%)")
    print(f"Company name not found: {not_found_count} ({not_found_count/len(domains)*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/len(domains)*100:.1f}%)")
    
    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    return results

def add_domains_with_status():
    """
    Add new domains with extraction status to the existing results
    """
    try:
        # Load existing results
        with open("test_extraction_results.json", 'r') as f:
            existing_results = json.load(f)
        
        # Get domains that already have results
        processed_domains = {r["domain"] for r in existing_results}
        print(f"Found {len(processed_domains)} already processed domains")
        
        # Add some new test domains
        new_domains = [
            "example.com",
            "google.com",
            "microsoft.com",
            "apple.com",
            "amazon.com",
            "facebook.com",
            "twitter.com",
            "linkedin.com",
            "github.com",
            "stackoverflow.com"
        ]
        
        # Filter out domains that have already been processed
        domains_to_process = [d for d in new_domains if d not in processed_domains]
        print(f"Found {len(domains_to_process)} new domains to process")
        
        if not domains_to_process:
            print("No new domains to process")
            return
        
        # Run extraction on new domains
        new_results = test_extraction(domains_to_process, "new_extraction_results.json")
        
        # Combine results
        combined_results = existing_results + new_results
        
        # Save combined results
        with open("combined_extraction_results.json", 'w') as f:
            json.dump(combined_results, f, indent=2)
        
        print(f"Combined results saved with {len(combined_results)} total domains")
        
    except FileNotFoundError:
        print("No existing results file found. Run test_extraction() first.")
    except Exception as e:
        print(f"Error: {str(e)}")

def analyze_results(results_file="test_extraction_results.json"):
    """
    Analyze extraction results to find patterns and common issues
    
    Args:
        results_file: Path to results file
    """
    try:
        # Load results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        print(f"Analyzing {len(results)} results")
        
        # Group domains by TLD
        tlds = {}
        for result in results:
            domain = result["domain"]
            tld = domain.split('.')[-1]
            if tld not in tlds:
                tlds[tld] = {
                    "total": 0,
                    "success": 0,
                    "not_found": 0,
                    "error": 0
                }
            
            tlds[tld]["total"] += 1
            
            if result["status"] == "error":
                tlds[tld]["error"] += 1
            elif result["status"] == "analyzed":
                if result["company_name"]:
                    tlds[tld]["success"] += 1
                else:
                    tlds[tld]["not_found"] += 1
        
        # Sort TLDs by total count
        sorted_tlds = sorted(tlds.items(), key=lambda x: x[1]["total"], reverse=True)
        
        print("\nResults by TLD:")
        for tld, counts in sorted_tlds:
            success_rate = counts["success"] / counts["total"] * 100 if counts["total"] > 0 else 0
            print(f"{tld}: {counts['total']} domains, {success_rate:.1f}% success rate")
        
        # Analyze company name patterns
        company_suffixes = {}
        for result in results:
            if result["status"] == "analyzed" and result["company_name"]:
                company = result["company_name"]
                
                # Extract legal suffix if present
                suffixes = ["Ltd", "Limited", "LLC", "Inc", "Corp", "Corporation", "GmbH", "B.V.", "Pty Ltd", "S.A."]
                found_suffix = None
                for suffix in suffixes:
                    if company.endswith(suffix) or f" {suffix}" in company:
                        found_suffix = suffix
                        break
                
                if found_suffix:
                    company_suffixes[found_suffix] = company_suffixes.get(found_suffix, 0) + 1
        
        # Sort suffixes by count
        sorted_suffixes = sorted(company_suffixes.items(), key=lambda x: x[1], reverse=True)
        
        print("\nMost common legal entity types:")
        for suffix, count in sorted_suffixes:
            percentage = count / sum(company_suffixes.values()) * 100
            print(f"{suffix}: {count} ({percentage:.1f}%)")
        
    except FileNotFoundError:
        print(f"Results file {results_file} not found")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test domains
TEST_DOMAINS = [
    "example.com",
    "python.org",
    "github.com",
    "stackoverflow.com",
    "wordpress.org",
    "apache.org",
    "mozilla.org",
    "jquery.com",
    "w3.org",
    "gnu.org"
]

if __name__ == "__main__":
    # Test extraction on a small set of domains
    test_extraction(TEST_DOMAINS)