import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)

COGNODB_URI = os.getenv("COGNODB_URI", "")
COGNODB_USERNAME = os.getenv("COGNODB_USERNAME", "")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Verify that basic database configuration exists
db_configured = bool(COGNODB_URI and COGNODB_USERNAME and COGNODB_PASSWORD)
