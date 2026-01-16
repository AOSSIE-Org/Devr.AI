import logging
import os
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

GITHUB_ORG = os.getenv("GITHUB_ORG", "Aossie-org")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

raw_batch_size = os.getenv("EMBEDDING_MAX_BATCH_SIZE", "32")
try:
    MAX_BATCH_SIZE = int(raw_batch_size)
    if MAX_BATCH_SIZE <= 0:
        raise ValueError
except ValueError:
    logger.warning("Invalid EMBEDDING_MAX_BATCH_SIZE '%s'. Defaulting to 32.", raw_batch_size)
    MAX_BATCH_SIZE = 32

EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
