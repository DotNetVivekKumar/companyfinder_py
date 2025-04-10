"""
Mock database for domain status tracking
"""
import json
import os
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initial mock data
INITIAL_DOMAINS = [
    {"domain": "ettaloves.com", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:00:00"},
    {"domain": "weblegs.co.uk", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:05:00"},
    {"domain": "www.just-keepers.com", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:10:00"},
    {"domain": "www.racketworld.co.uk", "status": "pending", "company_name": None, "contact_url": None, "last_updated": "2023-03-20T12:15:00"}
]

class MockDatabase:
    # Class-level variable to store domains in memory across instances
    _domains_cache = None
    
    def __init__(self, db_file="domains_db.json", use_memory=True):
        self.db_file = db_file
        self.use_memory = use_memory
        logger.info(f"Initializing MockDatabase (memory_mode: {use_memory})")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Initialize the database either in memory or file"""
        try:
            # If we're using memory and cache already exists, we're done
            if self.use_memory and MockDatabase._domains_cache is not None:
                logger.info("Using existing in-memory database")
                return
                
            # If using memory but no cache exists yet, initialize it
            if self.use_memory:
                logger.info("Initializing in-memory database")
                MockDatabase._domains_cache = INITIAL_DOMAINS.copy()
                return
                
            # Otherwise fall back to file-based database
            if not os.path.exists(self.db_file):
                logger.info(f"Creating file database at {self.db_file}")
                try:
                    with open(self.db_file, 'w') as f:
                        json.dump(INITIAL_DOMAINS, f, indent=2)
                except Exception as e:
                    logger.error(f"Error creating database file: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Fall back to memory mode
                    logger.info("Falling back to memory mode")
                    self.use_memory = True
                    MockDatabase._domains_cache = INITIAL_DOMAINS.copy()
        except Exception as e:
            logger.error(f"Critical error in _ensure_db_exists: {str(e)}")
            logger.error(traceback.format_exc())
            # Fall back to memory mode
            self.use_memory = True
            if MockDatabase._domains_cache is None:
                MockDatabase._domains_cache = INITIAL_DOMAINS.copy()
    
    def get_all_domains(self):
        """Get all domains from the database"""
        try:
            if self.use_memory:
                logger.info(f"Getting all domains from memory ({len(MockDatabase._domains_cache)})")
                return MockDatabase._domains_cache.copy()
                
            logger.info(f"Getting all domains from file {self.db_file}")
            try:
                with open(self.db_file, 'r') as f:
                    domains = json.load(f)
                logger.info(f"Retrieved {len(domains)} domains from file")
                return domains
            except Exception as e:
                logger.error(f"Error reading database file: {str(e)}")
                logger.error(traceback.format_exc())
                # Fall back to memory mode
                self.use_memory = True
                return MockDatabase._domains_cache.copy() if MockDatabase._domains_cache else []
        except Exception as e:
            logger.error(f"Error in get_all_domains: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def get_domain(self, domain):
        """Get a specific domain by name"""
        try:
            logger.info(f"Getting domain: {domain}")
            domains = self.get_all_domains()
            for d in domains:
                if d["domain"] == domain:
                    logger.info(f"Found domain: {domain}")
                    return d
            logger.info(f"Domain not found: {domain}")
            return None
        except Exception as e:
            logger.error(f"Error getting domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def add_domain(self, domain):
        """Add a new domain to the database"""
        try:
            logger.info(f"Adding domain: {domain}")
            
            # Check if domain already exists
            if self.get_domain(domain):
                logger.info(f"Domain {domain} already exists")
                return False  # Domain already exists
            
            # Get all domains
            domains = self.get_all_domains()
            
            # Create new domain object
            new_domain = {
                "domain": domain,
                "status": "pending",
                "company_name": None,
                "contact_url": None,
                "last_updated": datetime.now().isoformat()
            }
            
            # Add to list
            domains.append(new_domain)
            
            # Save changes
            if self.use_memory:
                MockDatabase._domains_cache = domains
                logger.info(f"Added domain {domain} to memory database")
            else:
                try:
                    with open(self.db_file, 'w') as f:
                        json.dump(domains, f, indent=2)
                    logger.info(f"Added domain {domain} to file database")
                except Exception as e:
                    logger.error(f"Error writing to database file: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Fall back to memory mode
                    self.use_memory = True
                    MockDatabase._domains_cache = domains
                    logger.info("Switched to memory mode")
            
            return True
        except Exception as e:
            logger.error(f"Error adding domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def update_domain(self, domain, status=None, company_name=None, contact_url=None):
        """Update an existing domain's information"""
        try:
            logger.info(f"Updating domain {domain} with status={status}, company_name={company_name}, contact_url={contact_url}")
            
            # Get all domains
            domains = self.get_all_domains()
            updated = False
            
            # Find and update the domain
            for d in domains:
                if d["domain"] == domain:
                    if status:
                        d["status"] = status
                    if company_name is not None:  # Allow empty string
                        d["company_name"] = company_name
                    if contact_url is not None:  # Allow empty string
                        d["contact_url"] = contact_url
                    d["last_updated"] = datetime.now().isoformat()
                    updated = True
                    break
            
            # Save if updated
            if updated:
                if self.use_memory:
                    MockDatabase._domains_cache = domains
                    logger.info(f"Updated domain {domain} in memory database")
                else:
                    try:
                        with open(self.db_file, 'w') as f:
                            json.dump(domains, f, indent=2)
                        logger.info(f"Updated domain {domain} in file database")
                    except Exception as e:
                        logger.error(f"Error writing to database file: {str(e)}")
                        logger.error(traceback.format_exc())
                        # Fall back to memory mode
                        self.use_memory = True
                        MockDatabase._domains_cache = domains
                        logger.info("Switched to memory mode during update")
            else:
                logger.info(f"Domain {domain} not found for update")
            
            return updated
        except Exception as e:
            logger.error(f"Error updating domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def delete_domain(self, domain):
        """Delete a domain from the database"""
        try:
            logger.info(f"Deleting domain: {domain}")
            
            # Get all domains
            domains = self.get_all_domains()
            initial_count = len(domains)
            
            # Filter out the domain to delete
            domains = [d for d in domains if d["domain"] != domain]
            
            # Check if any domain was removed
            if len(domains) < initial_count:
                if self.use_memory:
                    MockDatabase._domains_cache = domains
                    logger.info(f"Deleted domain {domain} from memory database")
                else:
                    try:
                        with open(self.db_file, 'w') as f:
                            json.dump(domains, f, indent=2)
                        logger.info(f"Deleted domain {domain} from file database")
                    except Exception as e:
                        logger.error(f"Error writing to database file: {str(e)}")
                        logger.error(traceback.format_exc())
                        # Fall back to memory mode
                        self.use_memory = True
                        MockDatabase._domains_cache = domains
                        logger.info("Switched to memory mode during delete")
                return True
            
            logger.info(f"Domain {domain} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return False