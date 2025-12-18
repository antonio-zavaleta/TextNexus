import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

# Constants relative to this file
# Assumes this file is in tests/utils/, so dataset is at ../data/golden_dataset/
BASE_DIR = Path(__file__).parent.parent / "data" / "golden_dataset"
DOCS_DIR = BASE_DIR / "documents"
GROUND_TRUTH_PATH = BASE_DIR / "ground_truth.json"

def load_golden_dataset() -> List[Dict[str, Any]]:
    """
    Loads the golden dataset Q&A pairs and verifies that referenced source files exist.

    Returns:
        List[Dict[str, Any]]: A list of dictionary objects representing the ground truth data.
    
    Raises:
        FileNotFoundError: If the ground_truth.json or any referenced PDF is missing.
    """
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(f"Ground truth file not found at: {GROUND_TRUTH_PATH}")

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate file references
    for item in data:
        files = item.get("ground_truth_context_files", [])
        for filename in files:
            file_path = DOCS_DIR / filename
            if not file_path.exists():
                logger.error(f"Missing source file: {file_path}")
                raise FileNotFoundError(f"Source file referenced in ground truth not found: {filename}")

    logger.info(f"Successfully loaded {len(data)} items from golden dataset.")
    return data

if __name__ == "__main__":
    # Self-test when run as a script
    logging.basicConfig(level=logging.INFO)
    try:
        items = load_golden_dataset()
        print(f"✅ Verified {len(items)} items and their file references.")
    except Exception as e:
        print(f"❌ Dataset validation failed: {e}")
        exit(1)
