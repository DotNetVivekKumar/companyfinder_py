"""
Main application file for the domain analysis service
"""
import os
import logging
import sys
from domain_api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Application starting...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
logger.info(f"Environment variables: {[key for key in os.environ.keys() if key.startswith(('PORT', 'PYTHON', 'ENABLE'))]}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting web server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)