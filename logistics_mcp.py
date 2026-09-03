# logistics_mcp.py - the AfyaPlus logistics MCP server
import json
import logging
import math
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("logistics")

mcp = FastMCP("afyaplus-logistics")

with open("clinic.json") as f:
    CLINICS = json.load(f)["clinics"]

VALID_ITEMS = ["amoxicillin", "ors_sachets", "malaria_kits"]

def distance_km(a: dict, b: dict) -> float:
    """Rough distance between two clinics in kilometres."""
    dx = (a["lon"] - b["lon"]) * 111.32 * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    dy = (a["lat"] - b["lat"]) * 110.57
    return round(math.sqrt(dx * dx + dy * dy), 1)

@mcp.tool()
def check_stock(item: str) -> str:
    """Check how many units of a medical item each clinic holds.
    Valid items: amoxicillin, ors_sachets, malaria_kits."""
    log.info("tool=check_stock item=%s", item)
    if item not in VALID_ITEMS:
        return json.dumps({"error": f"Unknown item '{item}'. Valid items: {VALID_ITEMS}"})
    rows = [
        {"clinic": c["name"], "county": c["county"], "units": c["stock"][item],
         "reorder_needed": c["stock"][item] < 10}
        for c in CLINICS
    ]
    return json.dumps({"item": item, "stock": rows})

@mcp.tool()
def plan_delivery_route(start_clinic_id: str) -> str:
    """Plan a delivery route visiting every clinic, starting from one clinic.
    Uses the nearest-neighbour rule: always drive to the closest unvisited clinic next.
    This is quick decision support, not a guaranteed-shortest route."""
    log.info("tool=plan_delivery_route start=%s", start_clinic_id)
    start = next((c for c in CLINICS if c["id"] == start_clinic_id), None)
    if start is None:
        ids = [c["id"] for c in CLINICS]
        return json.dumps({"error": f"Unknown clinic id '{start_clinic_id}'. Valid ids: {ids}"})
    route, remaining, total = [start], [c for c in CLINICS if c["id"] != start_clinic_id], 0.0
    while remaining:
        here = route[-1]
        nearest = min(remaining, key=lambda c: distance_km(here, c))
        total += distance_km(here, nearest)
        route.append(nearest)
        remaining.remove(nearest)
    return json.dumps({
        "route": [c["name"] for c in route],
        "total_km": round(total, 1),
        "method": "nearest-neighbour heuristic",
    })

@mcp.tool()
def get_delivery_eta(from_clinic_id: str, to_clinic_id: str) -> str:
    """Estimate driving distance (km) and time (minutes) between two clinics,
    assuming a 40 km/h average speed on regional roads."""
    log.info("tool=get_delivery_eta from=%s to=%s", from_clinic_id, to_clinic_id)
    a = next((c for c in CLINICS if c["id"] == from_clinic_id), None)
    b = next((c for c in CLINICS if c["id"] == to_clinic_id), None)
    if a is None or b is None:
        ids = [c["id"] for c in CLINICS]
        return json.dumps({"error": f"Unknown clinic id. Valid ids: {ids}"})
    km = distance_km(a, b)
    return json.dumps({"from": a["name"], "to": b["name"],
                       "km": km, "eta_minutes": round(km / 40 * 60)})

@mcp.resource("clinics://directory")
def clinic_directory() -> str:
    """Read-only directory of all AfyaPlus partner clinics."""
    return json.dumps([{"id": c["id"], "name": c["name"], "county": c["county"]} for c in CLINICS])

if __name__ == "__main__":
    mcp.run(transport="stdio")
    
