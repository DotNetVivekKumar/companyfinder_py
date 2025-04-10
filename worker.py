import time
import random
import logging
import os
import sys
import traceback
from mock_db import MockDatabase

# Configure logging - make sure it's very verbose
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_domains_once():
    """Process domains once without looping"""
    logger.info("Starting one-time domain processing...")
    
    try:
        # Initialize database with in-memory mode
        logger.info("Initializing database...")
        db = MockDatabase(use_memory=True)
        logger.info("Database initialized successfully")
        
        # Get all domains
        try:
            domains = db.get_all_domains()
            logger.info(f"Found {len(domains)} total domains in database")
        except Exception as e:
            logger.error(f"Error getting domains: {str(e)}")
            logger.error(traceback.format_exc())
            return
        
        # Get all domains, not just pending
        all_domains = [d["domain"] for d in domains]
        logger.info(f"Processing all domains regardless of status: {all_domains}")
        
        if not all_domains:
            logger.info("No domains to process")
            return
        
        # Process each domain
        for domain in all_domains:
            logger.info(f"Processing domain: {domain}")
            try:
                # Create test data for the domain
                company_name = f"Company for {domain}"
                contact_url = f"https://{domain}/contact"
                
                # Basic analysis without using the full analyzer
                result = {
                    "domain": domain,
                    "status": "analyzed",
                    "company_name": company_name,
                    "contact_url": contact_url
                }
                
                # Update database
                db.update_domain(
                    domain=domain,
                    status=result["status"],
                    company_name=result["company_name"],
                    contact_url=result["contact_url"]
                )
                
                logger.info(f"Updated {domain} with company: {company_name}, contact: {contact_url}")
                
            except Exception as e:
                logger.error(f"Error processing {domain}: {str(e)}")
                logger.error(traceback.format_exc())
        
        logger.info("One-time domain processing complete")
        
    except Exception as e:
        logger.error(f"Critical error in process_domains_once: {str(e)}")
        logger.error(traceback.format_exc())

# MAIN SCRIPT ENTRY POINT
if __name__ == "__main__":
    logger.info("Worker script started directly")
    try:
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir('.')}")
        
        # Print environment variables for debugging
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith(('PATH', 'PYTHONPATH'))}
        logger.info(f"Environment variables: {env_vars}")
        
        # Process immediately three times to ensure it works
        logger.info("PROCESSING DOMAINS - ATTEMPT 1")
        process_domains_once()
        
        logger.info("PROCESSING DOMAINS - ATTEMPT 2")
        process_domains_once()
        
        logger.info("PROCESSING DOMAINS - ATTEMPT 3")
        process_domains_once()
        
        # Then run periodically with short interval
        logger.info("Entering periodic processing mode")
        interval = 15  # seconds
        
        while True:
            logger.info(f"Sleeping for {interval} seconds before next processing...")
            time.sleep(interval)
            logger.info("PERIODIC PROCESSING - Waking up to process domains again")
            process_domains_once()
            
    except Exception as e:
        logger.error(f"Fatal error in worker: {str(e)}")
        logger.error(traceback.format_exc())