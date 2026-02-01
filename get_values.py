# citation
# https://github.com/poliastro/poliastro/blob/main/src/poliastro/bodies.py

import numpy as np
import pandas as pd
from datetime import datetime

class SolarSystemEngine:
    def __init__(self):
        # J2000: a(AU), e, i(deg), L(deg), Argument of Periapsis(deg), Longitude of Ascending Node(deg)
        self.elements = {
            "Mercury": [0.38709893, 0.20563069, 7.00487, 252.25084, 77.45645, 48.33167],
            "Venus":   [0.72333199, 0.00677323, 3.39471, 181.97973, 131.53298, 76.68069],
            "Earth":   [1.00000011, 0.01671022, 0.00005, 100.46435, 102.94719, 0.0],
            "Mars":    [1.52366231, 0.09341233, 1.85061, -4.55343, 336.04084, 49.57854],
            "Jupiter": [5.20336301, 0.04839266, 1.30530, 34.40438, 14.75385, 100.55615],
            "Saturn":  [9.53707032, 0.05415060, 2.48446, 49.94432, 92.43194, 113.71504],
            "Uranus":  [19.19126393, 0.04716771, 0.76986, 313.23218, 170.96424, 74.22988],
            "Neptune": [30.06896348, 0.00858587, 1.76917, 304.88003, 44.97135, 131.72169],
            "Pluto":   [39.48168677, 0.24880766, 17.14175, 238.92881, 224.06676, 110.30347],
            "Ceres":   [2.767, 0.0758, 10.59, 153.23, 73.06, 80.30]
        }
        self.AU = 149597870.7  # km
        self.MU_SUN = 1.32712440018e11  # km^3/s^2

    def _kepler_equation(self, M, e, tol=1e-8, max_iter=20):
        """Solve Kepler's equation iteratively"""
        E = M
        for _ in range(max_iter):
            dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            E = E - dE
            if abs(dE) < tol:
                break
        return E

    def get_position_velocity(self, body_name, date_str):
        """Returns both position (km) and velocity (km/s) vectors"""
        if body_name not in self.elements:
            raise ValueError(f"Unknown body: {body_name}")
        
        # Parse date
        d0 = datetime(2000, 1, 1, 12, 0)
        target_date = datetime.strptime(date_str, "%d%m%y")
        diff_days = (target_date - d0).total_seconds() / (24 * 3600)
        
        # Get orbital elements
        a_au, e, i_deg, L_deg, lp_deg, ln_deg = self.elements[body_name]
        a = a_au * self.AU  # Convert to km
        i, L, lp, ln = map(np.radians, [i_deg, L_deg, lp_deg, ln_deg])
        
        # Argument of perihelion and Mean Anomaly
        w = lp - ln
        M0 = L - lp
        
        # Mean motion (rad/day)
        n = np.sqrt(self.MU_SUN / a**3) * 86400  # Convert to rad/day
        
        # Current mean anomaly
        M = (M0 + n * diff_days) % (2 * np.pi)
        
        # Solve for Eccentric Anomaly
        E = self._kepler_equation(M, e)
        
        # Position in orbital plane
        x_orb = a * (np.cos(E) - e)
        y_orb = a * np.sqrt(1 - e**2) * np.sin(E)
        
        # Velocity in orbital plane (using vis-viva equation components)
        vx_orb = -np.sqrt(self.MU_SUN * a) / np.linalg.norm([x_orb, y_orb, 0]) * np.sin(E)
        vy_orb = np.sqrt(self.MU_SUN * a) / np.linalg.norm([x_orb, y_orb, 0]) * np.sqrt(1 - e**2) * np.cos(E)
        
        # Rotation matrices to heliocentric ecliptic coordinates
        cos_w, sin_w = np.cos(w), np.sin(w)
        cos_ln, sin_ln = np.cos(ln), np.sin(ln)
        cos_i, sin_i = np.cos(i), np.sin(i)
        
        # Position transformation
        x = (cos_ln * cos_w - sin_ln * sin_w * cos_i) * x_orb + \
            (-cos_ln * sin_w - sin_ln * cos_w * cos_i) * y_orb
        y = (sin_ln * cos_w + cos_ln * sin_w * cos_i) * x_orb + \
            (-sin_ln * sin_w + cos_ln * cos_w * cos_i) * y_orb
        z = (sin_w * sin_i) * x_orb + (cos_w * sin_i) * y_orb
        
        # Velocity transformation
        vx = (cos_ln * cos_w - sin_ln * sin_w * cos_i) * vx_orb + \
             (-cos_ln * sin_w - sin_ln * cos_w * cos_i) * vy_orb
        vy = (sin_ln * cos_w + cos_ln * sin_w * cos_i) * vx_orb + \
             (-sin_ln * sin_w + cos_ln * cos_w * cos_i) * vy_orb
        vz = (sin_w * sin_i) * vx_orb + (cos_w * sin_i) * vy_orb
        
        position = np.array([x, y, z])
        velocity = np.array([vx, vy, vz])
        
        return position, velocity

def main():
    engine = SolarSystemEngine()
    test_date = "230126" 
    
    results = []
    for body in engine.elements.keys():
        pos, vel = engine.get_position_velocity(body, test_date)
        results.append({
            "Body": body,
            "X (km)": f"{pos[0]:,.0f}",
            "Y (km)": f"{pos[1]:,.0f}",
            "Z (km)": f"{pos[2]:,.0f}",
            "Vx (km/s)": f"{vel[0]:.3f}",
            "Vy (km/s)": f"{vel[1]:.3f}",
            "Vz (km/s)": f"{vel[2]:.3f}"
        })
    
    df = pd.DataFrame(results)
    print("=== PLANETARY STATE VECTORS (HELIOCENTRIC) ===")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()