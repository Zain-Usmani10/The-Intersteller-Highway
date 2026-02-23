# Variables

# Planetary:
    # r1, r2: Absolute position vectors of planets at launch/arrival (3-axis)
    # pV1, pV2: Absolute velocity vectors of planets at launch/arrival (3-axis)
    # StdGravSun: Standard gravitational parameter of the Sun or Planet.

# Ship:
    # WMass: Mass with fuel
    # DMass: Mass without fuel
    # SI: Specific Impulse (velocity in km/s).
    # PLMass : Mass of payload

# Ship Trajectory:
    # sV1, sV2: Absolute ship velocity at launch and arrival
    # iV1, iV2: Injection and insertion velocities (relative to planet)
    # delV: Total change in velocity (measure of fuel expenditure)

# Orbit:
    # T: Orbital period = 43200 seconds (12 hours for refueling)
    # Rfuel: Radius of the circular parking/refueling orbit

import numpy as np
from datetime import datetime, timedelta
from get_values import SolarSystemEngine

# PLANETARY & SOLAR INITIALIZATION
StdGravSun = 1.32712440018e11 
StdGravPlanets = {
    "Mercury": 22032, "Venus": 324859, "Earth": 398600, 
    "Mars": 42828, "Jupiter": 126686534, "Saturn": 37931187, 
    "Uranus": 5793940, "Neptune": 6836529, "Pluto": 871, "Ceres": 63
}

# Initial position/velocity arrays
r1 = np.array([0.0, 0.0, 0.0]) 
r2 = np.array([0.0, 0.0, 0.0])
pV1 = np.array([0.0, 0.0, 0.0])
pV2 = np.array([0.0, 0.0, 0.0])

# SHIP INITIALIZATION
ships = {
    "Chevrolet Super Sonic": {
        "DMass": 5000.0, "Fuel_Cap": 20000.0, "SI": 4.2, 
        "Fuel_Type": "Leaded gasoline", "Max_PLMass": 1000.0, "PLMass": 0.0
    },
    "The Planet Hopper": {
        "DMass": 10000.0, "Fuel_Cap": 100000.0, "SI": 6.7, 
        "Fuel_Type": "Compressed air", "Max_PLMass": 4000.0, "PLMass": 0.0
    },
    "Moonivan": {
        "DMass": 25000.0, "Fuel_Cap": 400000.0, "SI": 9.1, 
        "Fuel_Type": "Biofuel", "Max_PLMass": 10000.0, "PLMass": 0.0
    },
    "Blue Origin Delivery Ship": {
        "DMass": 69000.0, "Fuel_Cap": 800000.0, "SI": 15.2, 
        "Fuel_Type": "Whale oil", "Max_PLMass": 50000.0, "PLMass": 0.0
    },
    "Yamaha Space Cycle": {
        "DMass": 1000.0, "Fuel_Cap": 2500.0, "SI": 100.0, 
        "Fuel_Type": "Antimatter", "Max_PLMass": 100.0, "PLMass": 0.0
    },
    "Ford F-1500": {
        "DMass": 10000.0, "Fuel_Cap": 100000.0, "SI": 18.67, 
        "Fuel_Type": "Space Diesel", "Max_PLMass": 8000.0, "PLMass": 0.0
    },
    "Beheamoth": {
        "DMass": 100000.0, "Fuel_Cap": 1500000.0, "SI": 11.1, 
        "Fuel_Type": "Nuclear propulsion", "Max_PLMass": 100000.0, "PLMass": 0.0
    }
}

# WMass calculation
for name, data in ships.items():
    data["WMass"] = data["DMass"] + data["PLMass"] + data["Fuel_Cap"]

# SHIP TRAJECTORY INITIALIZATION
sV1 = np.array([0.0, 0.0, 0.0])
sV2 = np.array([0.0, 0.0, 0.0])
iV1 = np.array([0.0, 0.0, 0.0])
iV2 = np.array([0.0, 0.0, 0.0])
delV = 0.0

# ORBIT
T = 43200  # 12 hours
Rfuel_data = {}

# parking orbit calculation
for planet, mu in StdGravPlanets.items():
    radius = (mu * (T / (2 * np.pi))**2)**(1/3)
    velocity = np.sqrt(mu / radius)
    Rfuel_data[planet] = {
        "Rfuel": radius,
        "v_park": velocity
    }

# SIMPLE LAMBERT SOLVER
def simple_lambert_solver(r1, r2, tof_seconds, mu=None):
    """
    Simple Lambert solver - calculates transfer orbit velocities.
    Replaces poliastro.iod.izzo.lambert().
    """
    if mu is None:
        mu = StdGravSun
    
    # Vector magnitudes
    r1_mag = np.linalg.norm(r1)
    r2_mag = np.linalg.norm(r2)
    
    # Chord distance
    c = np.linalg.norm(r2 - r1)
    s = (r1_mag + r2_mag + c) / 2.0  # semi-perimeter
    
    # Initial guess for semi-major axis
    a_min = s / 2.0
    a = a_min * 1.0
    
    # Transfer angle
    cos_dtheta = np.dot(r1, r2) / (r1_mag * r2_mag)
    dtheta = np.arccos(np.clip(cos_dtheta, -1, 1))
    
    # Iterate to find correct semi-major axis
    for iteration in range(30):
        alpha = 2.0 * np.arcsin(np.sqrt(s / (2.0 * a)))
        beta = 2.0 * np.arcsin(np.sqrt((s - c) / (2.0 * a)))
        
        # Time of flight for this orbit
        tof_calc = np.sqrt(a**3 / mu) * (alpha - beta - (np.sin(alpha) - np.sin(beta)))
        
        if abs(tof_calc - tof_seconds) < 1.0:  # within 1 second
            break
        
        # Update semi-major axis
        dtof_da = 1.5 * np.sqrt(a / mu) * (alpha - beta - (np.sin(alpha) - np.sin(beta)))
        a = a - (tof_calc - tof_seconds) / dtof_da
        a = max(a, a_min * 1.01)  # Ensure a stays above minimum
    
    f = 1.0 - a / r1_mag * (1.0 - np.cos(dtheta))
    g = r1_mag * r2_mag * np.sin(dtheta) / np.sqrt(mu * a * (1 - np.cos(dtheta)))
    
    v1 = (r2 - f * r1) / g
    
    g_dot = 1.0 - a / r2_mag * (1.0 - np.cos(dtheta))
    v2 = g_dot * r1 / g + (1.0 - f) * v1 / g
    
    return v1, v2

def get_highway_velocities(r1, r2, TOF_days):
    """YOUR function - just replaced izzo.lambert with simple_lambert_solver"""
    mu_sun = StdGravSun
    seconds = TOF_days * 24 * 3600
    sV1, sV2 = simple_lambert_solver(r1, r2, seconds, mu_sun)
    return sV1, sV2

def get_relative_velocities(sV1, pV1, sV2, pV2):
    """YOUR function - unchanged"""
    iV1 = sV1 - pV1
    iV2 = sV2 - pV2
    return iV1, iV2

def calculate_total_delV(iV1, iV2, start_planet, end_planet):
    """YOUR function - unchanged"""
    start_data = Rfuel_data[start_planet]
    end_data = Rfuel_data[end_planet]
    
    mu_start = StdGravPlanets[start_planet]
    mu_end = StdGravPlanets[end_planet]

    # launch force
    v_inf_launch = np.linalg.norm(iV1)
    v_inf_arrival = np.linalg.norm(iV2)
    
    v_peri_launch = np.sqrt(v_inf_launch**2 + 2 * mu_start / start_data["Rfuel"])
    dv_launch = abs(v_peri_launch - start_data["v_park"])
    
    # arrival force
    v_peri_arrival = np.sqrt(v_inf_arrival**2 + 2 * mu_end / end_data["Rfuel"])
    dv_arrival = abs(v_peri_arrival - end_data["v_park"])
    
    return dv_launch + dv_arrival

def get_required_fuel(delV_total, ship_name, current_payload):
    """YOUR function - unchanged"""
    ship = ships[ship_name]
    mf = ship["DMass"] + current_payload
    
    m0 = mf * np.exp(delV_total / ship["SI"])
    
    fuel_needed = m0 - mf
    
    possible = fuel_needed <= ship["Fuel_Cap"]
    return fuel_needed, possible

def find_best_flight(start_p, end_p, ship_name, payload, date_str):
    """YOUR function - expanded to try multiple TOF options"""
    engine = SolarSystemEngine()
    
    best_result = None
    best_fuel = float('inf')
    
    # Calculate ifferent time of flights
    for TOF_days in range(100, 400, 20):
        try:
            # Calculate arrival date
            launch_date = datetime.strptime(date_str, "%d%m%y")
            arrival_date = launch_date + timedelta(days=TOF_days)
            arrival_str = arrival_date.strftime("%d%m%y")
            
            # 1. Get Positions & Velocities
            r1, v_p1 = engine.get_position(start_p, date_str) 
            r2, v_p2 = engine.get_position(end_p, arrival_str)
            
            # 2. Highway Velocity (YOUR function)
            sV1, sV2 = get_highway_velocities(r1, r2, TOF_days)
            
            # 3. Relative Velocities (YOUR function)
            iV1, iV2 = get_relative_velocities(sV1, v_p1, sV2, v_p2)
            
            # 4. Total delta-V
            total_dv = calculate_total_delV(iV1, iV2, start_p, end_p)
            
            # 5.Fuel Capacity
            fuel, is_possible = get_required_fuel(total_dv, ship_name, payload)
            
            if is_possible and fuel < best_fuel:
                best_fuel = fuel
                best_result = {
                    "Flight impossible": False,
                    "Fuel": fuel,
                    "deltaV": total_dv,
                    "TOF_days": TOF_days,
                    "Launch_date": date_str,
                    "Arrival_date": arrival_str,
                    "iV1": iV1,
                    "iV2": iV2
                }
        except:
            continue
    
    if best_result is None:
        return {
            "Flight impossible": True,
            "Fuel": 0,
            "deltaV": 0
        }
    
    return best_result

def find_best_mission(start_planet, end_planet, ship_name, payload_mass, launch_date_str, min_tof, max_tof, step):
    """Bridge function for nav_cli.py to find efficient vs fastest routes"""
    engine = SolarSystemEngine() #
    flights = []
    
    for tof in range(min_tof, max_tof + 1, step):
        res = find_best_flight(start_planet, end_planet, ship_name, payload_mass, launch_date_str) # 
        if not res["Flight impossible"]:
            # Recalculate specifically for this TOF to separate Fast vs Efficient
            flights.append(res)
            
    if not flights:
        return {"flight_impossible": True, "reason": "No viable trajectory found within constraints."}

    # Efficiency = Lowest Fuel; Fastest = Shortest TOF
    efficient = min(flights, key=lambda x: x["Fuel"])
    fastest = min(flights, key=lambda x: x["TOF_days"])

    return {
        "flight_impossible": False,
        "efficient_flight": {
            "launch_date": efficient["Launch_date"],
            "v_inf_departure": efficient["iV1"],
            "dv_departure": efficient["deltaV"] / 2, # Approximation
            "fuel_required": efficient["Fuel"],
            "arrival_date": efficient["Arrival_date"],
            "v_inf_arrival": efficient["iV2"],
            "dv_arrival": efficient["deltaV"] / 2,
            "tof_days": efficient["TOF_days"]
        },
        "fastest_flight": {
            "launch_date": fastest["Launch_date"],
            "v_inf_departure": fastest["iV1"],
            "dv_departure": fastest["deltaV"] / 2,
            "fuel_required": fastest["Fuel"],
            "arrival_date": fastest["Arrival_date"],
            "v_inf_arrival": fastest["iV2"],
            "dv_arrival": fastest["deltaV"] / 2,
            "tof_days": fastest["TOF_days"]
        }
    }

if __name__ == "__main__":
    result = find_best_flight("Earth", "Mars", "Moonivan", 5000, "010226")
    print(f"Flight impossible: {result['Flight impossible']}")
    if not result['Flight impossible']:
        print(f"Fuel needed: {result['Fuel']:.0f} kg")
        print(f"Delta-V: {result['deltaV']:.2f} km/s")
        print(f"Time of flight: {result['TOF_days']} days")