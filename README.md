# The Interstellar Highway

## **Interstellar Trade Route Planner**
## OEC 2026 Programming Competition Entry

### Team
- Zain Usmani
- Abderrahmene Naceri
- Affan Syed
- Sadat Tanzim

---

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Libraries
The `requirements.txt` includes:
- `numpy==1.24.3` - Numerical computations and vector math
- `pygame==2.5.2` - GUI interface
- `pandas==2.0.3` - Data management

---

## Project Structure

```
project/
├── get_values.py                # Planetary position/velocity calculations
├── formula_implementation.py    # Mission physics & delta-v calculations
├── nav_cli.py                   # Command-line interface
├── game.py                      # GUI application (requires images/)
├── requirements.txt             # Python dependencies
└── images/                      # GUI assets (planets, backgrounds, etc.)
```

---

## Usage

### Command-Line Interface

```bash
python nav_cli.py <start> <dest> <ship> <payload> <earlier_launch_date> <latest_launch_date>
```

**Example:**
```bash
python nav_cli.py Earth Mars Moonivan 5000 010226 300626
```

**Parameters:**
- `start`: Departure planet (Mercury, Venus, Earth, Mars, Ceres, Jupiter, Saturn, Uranus, Neptune, Pluto)
- `dest`: Destination planet
- `ship`: Ship type (Chevrolet, Hopper, Moonivan, BlueOrigin, Yamaha, Ford, Beheamoth)
- `payload`: Payload mass in kg
- `launch_date`: Beginning of launch window in DDMMYY format
- `end_date`: End of launch window in DDMMYY format

**Output:** JSON with efficient and fastest flight parameters including:
- Launch date
- Launch vector (km/s)
- Delta-V requirements (km/s)
- Fuel consumption (kg)
- Arrival date
- Time of flight

### GUI Application

```bash
python game.py
```

**Note:** GUI requires `images/` directory with planet images and backgrounds.

### Testing Physics Engine

Test planetary calculations:
```bash
python get_values.py
```

Test mission analysis:
```bash
python formula_implementation.py
```

---

## Physics Implementation

### Core Calculations

1. **Orbital Mechanics** (`get_values.py`)
   - Kepler's equation solver for planetary positions
   - Velocity calculations from orbital elements
   - Heliocentric ecliptic coordinate transformations

2. **Mission Planning** (`formula_implementation.py`)
   - Lambert's problem solver (transfer orbit calculations)
   - Hyperbolic escape/capture delta-V
   - Tsiolkovsky rocket equation for fuel requirements
   - 12-hour parking orbit calculations

3. **Optimization**
   - Searches time-of-flight space (30-500 days)
   - Finds most fuel-efficient trajectory
   - Finds fastest arrival trajectory
   - Validates against ship fuel capacity

### Key Formulas

**Rocket Equation:**
```
ΔV = I_sp × ln(m_initial / m_final)
```

**Parking Orbit Radius (12-hour period):**
```
r = (μ × (T / 2π)²)^(1/3)
```

**Hyperbolic Excess Velocity:**
```
v_periapsis = √(v_∞² + 2μ/r)
```

---

## Competition Requirements Met

✅ **Requirement 1:** Users can input departure, destination, launch window, ship, payload  
✅ **Requirement 3:** Proper error handling for impossible flights  
✅ **Requirement 4:** Command-line interface  
✅ **Requirement 5:** Orbital data retrieval and path calculations  
✅ **Requirement 6:** GUI with visual trajectory display  

---

## Future Improvements

- Multi-stop trajectory optimization (gravity assists)
- Real-time orbital data from NASA Horizons
- Database storage of past routes
- Interactive 3D trajectory visualization
- Refueling stop calculations for long-range missions

---

## References

1. Orbital Mechanics - R.A. Braeunig (http://www.braeunig.us/space/)
2. GUI Implementation - 
3. Poliastro Library - Python astrodynamics (https://docs.poliastro.space/)
4. NASA JPL Horizons - Ephemeris data
5. Curtis, H.D. "Orbital Mechanics for Engineering Students"

---

## License

Created for OEC 2026 Programming Competition
