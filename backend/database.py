import logging
from neo4j import GraphDatabase
from backend import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_driver = None

def get_driver():
    global _driver
    if _driver is not None:
        return _driver
    
    if not config.db_configured:
        logger.error("Database credentials not fully specified in environment variables.")
        return None
    
    try:
        # Initialize standard Neo4j Bolt driver
        _driver = GraphDatabase.driver(
            config.COGNODB_URI,
            auth=(config.COGNODB_USERNAME, config.COGNODB_PASSWORD)
        )
        logger.info("Neo4j driver initialized successfully.")
        return _driver
    except Exception as e:
        logger.error(f"Failed to create Neo4j driver: {e}")
        return None

def verify_connection():
    driver = get_driver()
    if not driver:
        return False, "Driver not initialized. Verify your .env settings."
    try:
        # Run a simple query to verify connection
        with driver.session() as session:
            result = session.run("RETURN 1 AS val")
            record = result.single()
            if record and record["val"] == 1:
                return True, "Connected to CognoDB successfully."
            return False, "Verification query failed to return expected value."
    except Exception as e:
        logger.error(f"Connection verification failed: {e}")
        return False, str(e)

def close_driver():
    global _driver
    if _driver is not None:
        try:
            _driver.close()
            logger.info("Neo4j driver closed.")
        except Exception as e:
            logger.error(f"Failed to close Neo4j driver: {e}")
        _driver = None
