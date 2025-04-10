"""
Simple API for domain analysis
"""
from flask import Flask, jsonify, request
import os
import logging
import traceback
import sys
from mock_db import MockDatabase
from datetime import datetime
from simplified_analyzer import SimplifiedAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use in-memory database
db = MockDatabase(use_memory=True)
# Initialize analyzer
analyzer = SimplifiedAnalyzer()

@app.route('/')
def index():
    logger.info("Index endpoint called")
    return jsonify({
        "message": "Domain Analysis API",
        "endpoints": [
            "/api/domains - Get all domains or add a new one",
            "/api/domains/<domain> - Get, update or delete a specific domain",
            "/api/update-all - Run manual update on all domains",
            "/api/analyze/<domain> - Analyze a domain using real extraction logic",
            "/api/analyze-all - Analyze all domains using real extraction logic"
        ]
    })

@app.route('/api/domains', methods=['GET', 'POST'])
def domains():
    if request.method == 'GET':
        # Get all domains
        logger.info("GET /api/domains - Retrieving all domains")
        try:
            domains = db.get_all_domains()
            logger.info(f"Found {len(domains)} domains")
            return jsonify(domains)
        except Exception as e:
            logger.error(f"Error retrieving domains: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to retrieve domains"}), 500
    
    elif request.method == 'POST':
        # Add a new domain
        logger.info("POST /api/domains - Adding a new domain")
        try:
            data = request.get_json()
            if not data or 'domain' not in data:
                logger.warning("No domain provided in request")
                return jsonify({"error": "Domain name is required"}), 400
            
            domain = data['domain']
            logger.info(f"Adding domain: {domain}")
            
            success = db.add_domain(domain)
            
            if success:
                logger.info(f"Domain {domain} added successfully")
                return jsonify({"message": f"Domain {domain} added successfully"}), 201
            else:
                logger.warning(f"Domain {domain} already exists")
                return jsonify({"error": f"Domain {domain} already exists"}), 409
        except Exception as e:
            logger.error(f"Error adding domain: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to add domain"}), 500

@app.route('/api/domains/<domain>', methods=['GET', 'PUT', 'DELETE'])
def domain_detail(domain):
    logger.info(f"Request for domain: {domain}, method: {request.method}")
    
    if request.method == 'GET':
        # Get a specific domain
        logger.info(f"GET /api/domains/{domain}")
        try:
            domain_data = db.get_domain(domain)
            if domain_data:
                logger.info(f"Found domain: {domain}")
                return jsonify(domain_data)
            else:
                logger.warning(f"Domain {domain} not found")
                return jsonify({"error": f"Domain {domain} not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to retrieve domain"}), 500
    
    elif request.method == 'PUT':
        # Update a domain
        logger.info(f"PUT /api/domains/{domain}")
        try:
            data = request.get_json()
            status = data.get('status')
            company_name = data.get('company_name')
            contact_url = data.get('contact_url')
            
            logger.info(f"Updating domain {domain} with status={status}, company={company_name}, contact={contact_url}")
            
            success = db.update_domain(domain, status, company_name, contact_url)
            
            if success:
                logger.info(f"Domain {domain} updated successfully")
                return jsonify({"message": f"Domain {domain} updated successfully"})
            else:
                logger.warning(f"Domain {domain} not found")
                return jsonify({"error": f"Domain {domain} not found"}), 404
        except Exception as e:
            logger.error(f"Error updating domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to update domain"}), 500
    
    elif request.method == 'DELETE':
        # Delete a domain
        logger.info(f"DELETE /api/domains/{domain}")
        try:
            success = db.delete_domain(domain)
            
            if success:
                logger.info(f"Domain {domain} deleted successfully")
                return jsonify({"message": f"Domain {domain} deleted successfully"})
            else:
                logger.warning(f"Domain {domain} not found")
                return jsonify({"error": f"Domain {domain} not found"}), 404
        except Exception as e:
            logger.error(f"Error deleting domain {domain}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to delete domain"}), 500

@app.route('/api/update-all', methods=['GET'])
def update_all_domains():
    """Manually update all domains with test data"""
    logger.info("Manually updating all domains with test data")
    
    try:
        # Get all domains
        domains = db.get_all_domains()
        logger.info(f"Found {len(domains)} domains")
        
        updated_count = 0
        
        # Update each domain
        for domain_data in domains:
            domain = domain_data["domain"]
            company_name = f"Company for {domain} (via API)"
            contact_url = f"https://{domain}/contact"
            
            logger.info(f"Updating {domain} with company: {company_name}")
            
            # Update domain
            success = db.update_domain(
                domain=domain,
                status="analyzed",
                company_name=company_name,
                contact_url=contact_url
            )
            
            if success:
                updated_count += 1
        
        # Verify updates
        updated_domains = db.get_all_domains()
        result = {
            "message": f"Successfully updated {updated_count} domains",
            "domains": updated_domains
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error updating domains: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to update domains"}), 500

@app.route('/api/analyze/<domain>', methods=['GET'])
def analyze_domain_real(domain):
    """Analyze a domain using real extraction logic"""
    logger.info(f"Analyzing domain: {domain}")
    
    try:
        # Run analysis
        result = analyzer.analyze_domain(domain)
        
        # Add domain to database if it doesn't exist
        domain_data = db.get_domain(domain)
        if not domain_data:
            db.add_domain(domain)
        
        # Update database with results
        success = db.update_domain(
            domain=domain,
            status=result["status"],
            company_name=result["company_name"],
            contact_url=None  # Simplified analyzer doesn't extract contact URL
        )
        
        if success:
            logger.info(f"Successfully analyzed and updated domain: {domain}")
            return jsonify(result)
        else:
            logger.error(f"Failed to update domain {domain} after analysis")
            return jsonify({"error": "Failed to update domain after analysis"}), 500
            
    except Exception as e:
        logger.error(f"Error analyzing domain {domain}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to analyze domain",
            "details": str(e)
        }), 500

@app.route('/api/analyze-all', methods=['GET'])
def analyze_all_domains_real():
    """Analyze all domains using real extraction logic"""
    logger.info("Analyzing all domains")
    
    try:
        # Get all domains
        domains = db.get_all_domains()
        domain_list = [d["domain"] for d in domains]
        logger.info(f"Found {len(domains)} domains to analyze")
        
        # Run analysis
        results = analyzer.analyze_domains(domain_list)
        
        # Update database with results
        updated_count = 0
        for result in results:
            domain = result["domain"]
            success = db.update_domain(
                domain=domain,
                status=result["status"],
                company_name=result["company_name"],
                contact_url=None  # Simplified analyzer doesn't extract contact URL
            )
            if success:
                updated_count += 1
        
        # Return results
        return jsonify({
            "message": f"Successfully analyzed {updated_count} domains",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error analyzing domains: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to analyze domains",
            "details": str(e)
        }), 500

@app.route('/healthz', methods=['GET'])
def healthcheck():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)