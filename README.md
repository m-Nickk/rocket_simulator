# Rocket Physics Simulation 🚀

A 2D rocket flight simulator built with Python and Pygame. This project simulates realistic rocket kinematics and atmospheric flight, transitioning from sea level up into suborbital space.

## What's New (Major Upgrade)

I have completely overhauled the physics engine and graphics from my previous version. Here is what has changed:

*   **[New] Dynamic Atmosphere Model**: Replaced the constant vacuum environment with a multi-layered atmospheric model (Troposphere and Stratosphere). Air density ($\rho$) now drops realistically with altitude based on thermal lapse rates.
*   **[New] Mach-Dependent Aerodynamic Drag**: Implemented speed-of-sound tracking based on local air temperature. The rocket now calculates its current Mach number and dynamically shifts its drag coefficient ($C_d$) through subsonic, transonic, and supersonic regimes.
*   **[New] Variable Specific Impulse ($I_{sp}$)**: The engine's efficiency is no longer static. It dynamically interpolates between sea-level thrust and vacuum efficiency as atmospheric pressure drops.
*   **[New] True Gravitational Decay**: Gravity ($g$) is no longer locked at a constant $10\text{ m/s}^2$. It now drops accurately according to Newton's law of universal gravitation as the rocket gains altitude.
*   **[New] Advanced Visual FX & Parallax**:
    *   The background sky smoothly fades from bright day-blue to space-black based on altitude.
    *   Stars dynamically fade in and brighten as the atmosphere thins out.
    *   Added a fully animated, pulsing rocket exhaust flame using sine-wave scaling.
    *   The Earth's horizon now realistically curves away and drops as you fly higher.

---

## Mathematical & Physical Models Used

1. **Thrust Vectoring Equation:** 
   $$F_{thrust} = I_{sp}(altitude) \cdot g(altitude) \cdot \frac{dm}{dt}$$
2. **Aerodynamic Drag Force:** 
   $$F_{drag} = \frac{1}{2} \cdot \rho(h) \cdot v^2 \cdot C_d(Mach) \cdot A$$
3. **Newtonian Gravity Drop:** 
   $$g(h) = 9.81 \cdot \left(\frac{R_{earth}}{R_{earth} + h}\right)^2$$

---

## Installation & Controls

1. Clone this repository:
   ```bash
   git clone https://github.com
   ```
2. Install the required graphics library:
   ```bash
   pip install pygame
   ```
3. Run the simulator:
   ```bash
   python rocket_simulator.py
   ```

**Controls:**
*   `SPACEBAR` — Toggle Rocket Engine ON / OFF.

---

##  License
This project is licensed under the MIT License - feel free to use, modify, and build upon this code
