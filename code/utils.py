import json, os

# Load JSON files from the project's `co2_data/` folder
def load_json(name: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "co2_data")
    path = os.path.join(data_dir, name)
    if not os.path.exists(path):
        data_dir = os.path.join(base_dir, "data")
        path = os.path.join(data_dir, name)
    with open(path, "r") as f:
        return json.load(f)

# Normalize strings for comparison
def lowercase_clean(s: str) -> str:
    return " ".join(s.lower().strip().split())

# Convert grams to kilograms
def to_kg(weight_g: float) -> float:
    return max(0.0, float(weight_g)) / 1000.0

