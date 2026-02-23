"""
Command-line interface for interplanetary mission planning.
Usage: python nav_cli.py <start> <dest> <ship> <payload> <date1> <date2>
"""

import sys
import json
from formula_implementation import find_best_mission, SHIPS

def parse_ship_name(cli_input):
    """Convert CLI ship names to internal format"""
    mapping = {
        "chevrolet": "Chevrolet Super Sonic",
        "hopper": "The Planet Hopper",
        "moonivan": "Moonivan",
        "blueorigin": "Blue Origin Delivery Ship",
        "yamaha": "Yamaha Space Cycle",
        "ford": "Ford F-1500",
        "beheamoth": "Beheamoth"
    }
    
    cli_lower = cli_input.lower().replace("_", "").replace("-", "").replace(" ", "")
    
    for key, value in mapping.items():
        if key in cli_lower:
            return value
    
    # Try exact match
    for ship_name in SHIPS.keys():
        if cli_input.lower() in ship_name.lower():
            return ship_name
    
    raise ValueError(f"Unknown ship: {cli_input}")

def format_vector(vec):
    """Format numpy array as x,y,z string"""
    return f"{vec[0]:.3f},{vec[1]:.3f},{vec[2]:.3f}"

def main():
    if len(sys.argv) != 7:
        print("Usage: python nav_cli.py <start> <dest> <ship> <payload> <date1> <date2>")
        print("Example: python nav_cli.py Earth Mars Moonivan 5000 010226 300626")
        sys.exit(1)
    
    start_planet = sys.argv[1].capitalize()
    dest_planet = sys.argv[2].capitalize()
    ship_input = sys.argv[3]
    payload = float(sys.argv[4])
    launch_date = sys.argv[5]
    end_date = sys.argv[6]
    
    # Parse ship name
    try:
        ship_name = parse_ship_name(ship_input)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)
    
    # Run mission analysis
    try:
        result = find_best_mission(
            start_planet=start_planet,
            end_planet=dest_planet,
            ship_name=ship_name,
            payload_mass=payload,
            launch_date_str=launch_date,
            min_tof=50,
            max_tof=500,
            step=15
        )
        
        # Format output as JSON
        if result["flight_impossible"]:
            output = {
                "Flight impossible": True,
                "reason": result.get("reason", "Unknown")
            }
        else:
            eff = result["efficient_flight"]
            fast = result["fastest_flight"]
            
            output = {
                "Flight impossible": False,
                "Efficient flight parameters": {
                    "Launch date": eff["launch_date"],
                    "Launch vector": format_vector(eff["v_inf_departure"]),
                    "Launch deltaV": f"{eff['dv_departure']:.3f}",
                    "Fuel": f"{eff['fuel_required']:.0f}",
                    "Arrival date": eff["arrival_date"],
                    "Arrival vector": format_vector(eff["v_inf_arrival"]),
                    "Arrival deltaV": f"{eff['dv_arrival']:.3f}",
                    "Time of flight": f"{eff['tof_days']} days"
                },
                "Soonest arrival flight parameters": {
                    "Launch date": fast["launch_date"],
                    "Launch vector": format_vector(fast["v_inf_departure"]),
                    "Launch deltaV": f"{fast['dv_departure']:.3f}",
                    "Fuel": f"{fast['fuel_required']:.0f}",
                    "Arrival date": fast["arrival_date"],
                    "Arrival vector": format_vector(fast["v_inf_arrival"]),
                    "Arrival deltaV": f"{fast['dv_arrival']:.3f}",
                    "Time of flight": f"{fast['tof_days']} days"
                }
            }
        
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()