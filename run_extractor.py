"""
Script to run the company name extractor on specified domains
"""
import sys
import json
import argparse
import time
import random
from company_name_extractor import CompanyNameExtractor

def extract_from_domains(domains, output_file=None):
    """
    Extract company names from a list of domains
    
    Args:
        domains: List of domains to analyze
        output_file: Optional file to save results
    
    Returns:
        List of extraction results
    """
    extractor = CompanyNameExtractor()
    results = []
    
    print(f"Processing {len(domains)} domains...")
    
    for i, domain in enumerate(domains):
        print(f"[{i+1}/{len(domains)}] Analyzing {domain}")
        
        try:
            # Process the domain
            result = extractor.extract_company_name(domain)
            results.append(result)
            
            # Print results
            print(f"  Status: {result['status']}")
            print(f"  Company name: {result['company_name']}")
            
            # Save results after each domain if output file specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
            
            # Add delay between domains
            if i < len(domains) - 1:  # Skip delay after last domain
                delay = random.uniform(1, 3)
                print(f"  Waiting {delay:.2f} seconds before next domain...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"  Error analyzing {domain}: {str(e)}")
            results.append({
                "domain": domain,
                "status": "error",
                "company_name": None,
                "error": str(e)
            })
    
    # Save final results if output file specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    
    # Print summary
    success_count = sum(1 for r in results if r["status"] == "analyzed" and r["company_name"])
    error_count = sum(1 for r in results if r["status"] == "error")
    not_found_count = sum(1 for r in results if r["status"] == "analyzed" and not r["company_name"])
    
    print("\nExtraction summary:")
    print(f"Total domains: {len(domains)}")
    print(f"Successful extractions: {success_count} ({success_count/len(domains)*100:.1f}%)")
    print(f"Company name not found: {not_found_count} ({not_found_count/len(domains)*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/len(domains)*100:.1f}%)")
    
    return results

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="Extract company names from domains")
    
    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domains", nargs="+", help="List of domains to analyze")
    group.add_argument("-f", "--file", help="File containing domains, one per line")
    
    # Output options
    parser.add_argument("-o", "--output", help="Output JSON file for results")
    
    args = parser.parse_args()
    
    # Get domains from arguments or file
    if args.domains:
        domains = args.domains
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                domains = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading domains file: {str(e)}")
            return 1
    
    # Extract company names
    extract_from_domains(domains, args.output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())