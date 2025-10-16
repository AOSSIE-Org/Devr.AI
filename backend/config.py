from dotenv import load_dotenv, find_dotenv
import os


dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

GITHUB_ORG = os.getenv("GITHUB_ORG", "Aossie-org")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_BATCH_SIZE = int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", "32"))
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
