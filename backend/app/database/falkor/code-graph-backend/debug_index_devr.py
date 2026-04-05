import sys
import os
import logging
from pathlib import Path
from api.project import Project

# Configure logging to verify what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_indexing():
    repo_url = "https://github.com/AOSSIE-Org/Devr.AI"
    logger.info(f"Starting debug indexing for: {repo_url}")

    try:
    
        proj = Project.from_git_repository(repo_url)
        
        logger.info(f"Repository cloned to: {proj.path}")
        
        logger.info("Analyzing sources...")
        proj.analyze_sources()
        stats = proj.graph.stats()
        logger.info(f"Indexing complete. Stats: {stats}")
        
        if stats and stats.get('node_count', 0) > 0:
            logger.info("SUCCESS: Graph populated with nodes.")
        else:
            logger.error("FAILURE: Graph seems empty.")

    except Exception as e:
        logger.exception("An error occurred during indexing:")

if __name__ == "__main__":
    debug_indexing()
