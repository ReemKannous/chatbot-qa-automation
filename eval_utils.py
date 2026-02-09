import json
from pathlib import Path

def load_test_data(filename: str):
    path = Path(__file__).parent / "testdata" / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)
