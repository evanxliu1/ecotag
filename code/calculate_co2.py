"""
This script calculates the CO2 footprint for a garment based on the following inputs:
- materials (fabric production)
- manufacturing (country-based factor)
- washing/use phase (wash temperature + optional tumble drying + optional dry cleaning)

Data dependencies:
- co2_data/materials.json
- co2_data/manufacturing.json
- co2_data/washing.json

Assumptions / limitations:
- Assumes a 2-year lifetime via washes = 24 * washes_per_month (default 2).
- Assumes garment weight is 1kg/1000g.
- Transportation, packaging, and end-of-life disposal are not included.
- All results are returned in kg CO2e.
"""

from schemas import TagRecord, ScenarioResult
from utils import load_json, to_kg


class FactorRegistry:
    def __init__(self):
        self.materials = load_json("materials.json")
        self.mfg = load_json("manufacturing.json")
        self.washing = load_json("washing.json")

def estimate(record: TagRecord, preferred_mode="ship") -> ScenarioResult:
    fx = FactorRegistry()
    b = {}
    weight_g = record.weight_g or 1000  # Default 1kg
    weight_kg = to_kg(weight_g)

    # Materials (Fabric)
    # Use cotton as default if no materials are specified
    mat = 0
    for m in record.materials or []:
        f = fx.materials.get(m.fiber, fx.materials["cotton"])
        mat += (m.pct/100)*f["kgco2_per_kg"]
    b["materials"] = weight_kg * (mat or fx.materials["cotton"]["kgco2_per_kg"])

    # Manufacturing
    # Use China as default if country not found (common manufacturing location)
    country_key = (record.origin_country or "china").lower()
    mfg_f = fx.mfg.get(country_key, fx.mfg.get("china", {"kgco2_per_kg": 0.50}))
    b["manufacturing"] = weight_kg * mfg_f["kgco2_per_kg"]

    # Washing (Use phase)
    # Default to machine wash cold if no wash type is specified
    washes = int(24 * record.care.washes_per_month)
    
    # Determine wash type
    if record.care.wash == "cold":
        wash_key = "machine_wash_cold"
    elif record.care.wash == "warm":
        wash_key = "machine_wash_warm"
    elif record.care.wash == "hot":
        wash_key = "machine_wash_hot"
    else:
        wash_key = "machine_wash_cold"  # Default to cold
    
    washing = washes * fx.washing.get(wash_key, {"kgco2_per_use": 0.10})["kgco2_per_use"]
    
    # Add drying emissions
    if record.care.dry == "tumble":
        washing += washes * fx.washing.get("tumble_dry_medium", {"kgco2_per_use": 2.60})["kgco2_per_use"]
    
    # Add dry cleaning emissions if applicable
    if record.care.dry_clean and record.care.dry_clean != "none":
        washing += washes * fx.washing.get("dry_clean", {"kgco2_per_use": 0.40})["kgco2_per_use"]
    
    b["washing"] = washing

    total=sum(b.values())
    return ScenarioResult(total,b,{"weight_g":str(weight_g),"origin":record.origin_country or "unknown",
        "washes_lifetime":str(washes)})
