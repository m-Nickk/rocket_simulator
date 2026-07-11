import random
import pygame
import math

# Initialize Pygame modules
pygame.init()

# Template class for the rocket behavior and physics
class Rocket:
    def __init__(self, name, x, y, m0, mf, isp_sea_lvl, isp_vacuum, color, mkg, current_mass, current_cd, speed=0, g=9.81, altitude=0, A=0.35, r_earth = 6371000, v_sound = 340, mach = 0, flame_time = 0):
        self.name = name                  
        self.x = x                              # X coordinate on screen
        self.y = y                              # Y coordinate on screen
        self.m0 = m0                            # Total initial mass (wet mass) in kg
        self.mf = mf                            # Final mass (dry mass/empty rocket) in kg
        self.isp_sea_lvl = isp_sea_lvl          # Specific impulse at sea level (s)
        self.isp_vacuum = isp_vacuum            # Specific impulse in vacuum (s)
        self.color = color                      # RGB color tuple for rendering
        self.mkg = mkg                          # Fuel consumption rate (kg/s)
        self.speed = speed                      # Current vertical velocity (m/s)
        self.current_mass = current_mass        # Dynamic mass tracking during flight
        self.current_cd = current_cd            # Dynamic drag coefficient
        self.g = g                              # Gravitational acceleration variable
        self.engine_on = False                  # Engine state flag (True/False)
        self.altitude = altitude                # Flight altitude above sea level (meters)
        self.rho_0 = 1.225                      # Sea level air density (kg/m^3)
        self.scale_height = 8500                # Atmospheric scale height
        self.A = A                              # Cross-sectional reference area (m^2)
        self.r_earth = r_earth                  # Mean Earth radius in meters
        self.v_sound = v_sound                  # Speed of sound variable (m/s)
        self.mach = mach                        # Mach number variable
        self.flame_time = flame_time            # Timer for engine flame animation

    def update(self, dt):
        if dt <= 0:
            return

        # Advance engine flame timer
        self.flame_time += dt
        
        # Calculate ambient temperature based on troposphere thermal lapse rate
        if self.altitude < 11000:
           T = 288.15 - 0.0065 * self.altitude
        else:
            T = 216.65 # Constant temperature in the lower stratosphere
        
        # Update speed of sound in air based on local temperature
        self.v_sound = 20.05 * math.sqrt(T)

        # Calculate current Mach number
        self.mach = abs(self.speed) / self.v_sound

        # Determine dynamic drag coefficient (Cd) based on Mach number regimes
        if self.mach < 0.8:
            self.current_cd = 0.15 # Subsonic drag

        elif 0.8 <= self.mach < 1.1:
            progress = (self.mach - 0.8) / (1.1 - 0.8)
            self.current_cd = 0.15 + progress * (0.45 - 0.15) # Transonic drag rise

        elif 1.1 <= self.mach < 2.5:
            progress = (self.mach - 1.1) / (2.5 - 1.1)
            self.current_cd = 0.45 - progress * (0.45 - 0.28) # Supersonic drag decay

        else:
            self.current_cd = 0.28 # Hypersonic/High supersonic limit
             
        # Pre-calculate reference atmospheric densities for layer boundaries
        rho_11 = 1.225 * (216.65 / 288.15)**4.256
        rho_25 = rho_11 * math.exp(-(25000 - 11000) / 6341)

        # Calculate atmospheric air density (rho) using barometric formulas
        if self.altitude < 11000:
            rho = self.rho_0 * (T / 288.15)**4.256
        elif 11000 <= self.altitude < 25000:
            rho = rho_11 * math.exp(-(self.altitude - 11000) / 6341)
        else:
            rho = rho_25 * math.exp(-(self.altitude - 25000) / 6341)

        # Calculate aerodynamic drag force using the drag equation
        drag_force = 0.5 * rho * (self.speed ** 2) * self.current_cd * self.A
        # Linearly interpolate specific impulse (Isp) between sea level and vacuum
        self.current_isp = self.isp_vacuum - (self.isp_vacuum - self.isp_sea_lvl) * (rho / self.rho_0)
        # Apply Newton's law of universal gravitation for changing altitude
        self.g = 9.81 * (self.r_earth / (self.r_earth + self.altitude))** 2

        thrust = 0

        # Calculate engine thrust force if active and fuel is available
        if self.engine_on and (self.current_mass > self.mf):
            fuel_left = self.current_mass - self.mf
            fuel_wanted = self.mkg * dt
            fuel_to_burn = min(fuel_wanted, fuel_left)

            # Consume fuel mass
            self.current_mass -= fuel_to_burn

            # Auto-shutdown engine if out of fuel
            if self.current_mass <= self.mf + 1e-5:
                self.current_mass = self.mf
                self.engine_on = False

            # T = Isp * g * (dm/dt) thrust equation
            thrust = self.current_isp * self.g * (fuel_to_burn / dt)

        # Prevent floating point inaccuracy from dropping mass below dry weight
        if self.current_mass <= self.mf + 0.01:
            self.current_mass = float(self.mf)

        # Calculate gravitational force acting on the rocket
        gravity = self.current_mass * self.g

        # Compute net acceleration (Drag ALWAYS opposes the direction of motion)
        if self.speed > 0:
            acceleration = (thrust - gravity - drag_force) / self.current_mass
        else:
            acceleration = (thrust - gravity + drag_force) / self.current_mass 

        # Update flight kinematics (velocity and position)
        self.speed += acceleration * dt
        self.altitude += self.speed * dt

        # Handle ground collision boundary physics
        if self.altitude <= 0:
            self.altitude = 0
            if self.speed < 0:
                self.speed = 0
                self.engine_on = False

# Create the first rocket instance with configured mass and ISP specs
rocket_1 = Rocket(name="Rocket_1", x=440, y=600, m0=2000, mf=500, isp_sea_lvl=210, isp_vacuum=250, color=(200, 200, 200), mkg=25, current_mass=2000, speed=0, g=9.81, altitude=0, current_cd=0, A=0.35)

# Set up the pygame game window resolution
screen = pygame.display.set_mode((900, 900))

# Initialize the font rendering system
pygame.font.init()
font = pygame.font.SysFont("Arial", 16, bold=True)

# Main game loop controls and time tracking
clock = pygame.time.Clock()
running = True

# Generate background star positions for parallax effect
stars = []
for i in range(200):
    star_x = random.randint(0, 900)
    star_y = random.randint(0, 900)
    stars.append([star_x, star_y])

# Main application and rendering loop
while running:
    # Cap framerate to 60 FPS and get delta time in seconds
    dt = clock.tick(60) / 1000.0

    dynamic_length = 0
    
    # Process user input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle rocket engine on/off if fuel is left
                if rocket_1.current_mass > rocket_1.mf:
                    rocket_1.engine_on = not rocket_1.engine_on

    # Update rocket physics state
    rocket_1.update(dt)

    # Calculate remaining fuel percentage for the HUD bar
    max_fuel = rocket_1.m0 - rocket_1.mf
    current_fuel = max(0, rocket_1.current_mass - rocket_1.mf)
    fuel_ratio = current_fuel / max_fuel

    # Fade background sky color to black as rocket gains altitude
    factor = math.exp(-rocket_1.altitude / 10000)

    r = int(135 * factor)
    g = int(206 * factor)
    b = int(235 * factor)

    screen.fill((r, g, b))

    # Move and render stars (stars scroll down relative to rocket upward speed)
    for star in stars:
        star[1] += rocket_1.speed * dt * 0.03

        # Wrap star coordinates when they move off screen bounds
        if star[1] > 900:
            star[1] = 0
            star[0] = random.randint(0, 900)
        elif star[1] < 0:
            star[1] = 900
            star[0] = random.randint(0, 900)
        
        # Dynamically brighten stars as sky background darkens at high altitude
        star_factor = math.exp(-rocket_1.altitude / 35000)
        star_r = int(r + (255 - r) * (1 - star_factor))
        star_g = int(g + (255 - g) * (1 - star_factor))
        star_b = int(b + (255 - b) * (1 - star_factor))

        pygame.draw.circle(screen, (star_r, star_g, star_b), (int(star[0]), int(star[1])), 1)

    # Render planet Earth horizon curving away as altitude increases
    earth_y = 950 + (rocket_1.altitude * 0.05)
    pygame.draw.circle(screen, (30, 144, 255), (450, int(earth_y)), 400)

    # Compute a pulsing flame length using sine wave calculation
    if rocket_1.engine_on and (rocket_1.current_mass > rocket_1.mf):
        pulse = (math.sin(rocket_1.flame_time * 15) +1) / 2
        dynamic_length = 20 + pulse * 15

    # Define geometric vertices for the rocket nose cone
    nose_points = [
        (int(rocket_1.x), int(rocket_1.y)),
        (int(rocket_1.x + 3), int(rocket_1.y - 14)),
        (int(rocket_1.x + 10), int(rocket_1.y - 25)),
        (int(rocket_1.x + 17), int(rocket_1.y - 14)),
        (int(rocket_1.x + 20), int(rocket_1.y)), 
    ]

    # Draw the rocket nose cone and main fuselage body
    pygame.draw.polygon(screen, rocket_1.color, nose_points)
    pygame.draw.rect(screen, rocket_1.color, (int(rocket_1.x), int(rocket_1.y), 21, 50))

    # Prepare HUD state labels for the rocket engine status
    if rocket_1.engine_on:
        text_engine = font.render("Engine ON", True, (0, 120, 0))
    else:
        text_engine = font.render("Engine OFF", True, (160, 0, 0))
    
    # Draw animated propulsion exhaust flame if the engine is on
    if rocket_1.engine_on:
        flame_points = [
            (int(rocket_1.x), int(rocket_1.y + 50)),
            (int(rocket_1.x + 20), int(rocket_1.y + 50)),
            (int(rocket_1.x + 10), int(rocket_1.y + 50 + dynamic_length)),
            ]
        pygame.draw.polygon(screen, (255, 140, 0), flame_points)
    
    # Render dynamic flight telemetry text labels
    text_mass = font.render(f"Mass: {round(rocket_1.current_mass, 1)} kg", True, (255, 255, 255))
    text_speed = font.render(f"Speed: {round(rocket_1.speed, 1)} m/s", True, (255, 255, 255))
    text_altitude = font.render(f"Altitude: {round(rocket_1.altitude)} meters", True, (255, 255, 255))
    text_fuel_label = font.render("Fuel", True, (255, 255, 255))
    text_fuel_data = font.render(f"{round(rocket_1.current_mass - rocket_1.mf, 1)} kg", True, (255, 255, 255))
    text_current_isp = font.render(f"Current Isp: {round(rocket_1.current_isp, 1)} N", True, (255, 255, 255))
    text_mach = font.render(f"Mach: {round(rocket_1.mach, 2)}", True, (255, 255, 255))

    # Blit telemetry dashboard onto the screen coordinates
    screen.blit(text_mass, (10, 60))
    screen.blit(text_speed, (10, 83))
    screen.blit(text_altitude, (365, 30))
    screen.blit(text_fuel_label, (850, 100))
    screen.blit(text_fuel_data, (820, 275)) 
    screen.blit(text_current_isp, (743, 60))
    screen.blit(text_mach, (743, 80))
    screen.blit(text_engine, (10, 105))

    # Dimensions and settings for the fuel HUD indicator bar
    bar_x = 860
    bar_y = 120
    bar_width = 20
    bar_max_height = 150
    padding = 2

    # Draw the background slot and the dynamic white filler for fuel level
    pygame.draw.rect(screen, (70, 70, 70), (bar_x, bar_y, bar_width, bar_max_height))
    inner_max_height = bar_max_height - (padding * 2)
    current_bar_height = int(inner_max_height * fuel_ratio)
    dynamic_y = bar_y + padding + (inner_max_height - current_bar_height)
    inner_width = bar_width - (padding * 2)
    if current_bar_height > 0:
        pygame.draw.rect(screen, (255, 255, 255), (bar_x + padding, dynamic_y, inner_width, current_bar_height))

    # Refresh and flip the screen buffer display
    pygame.display.flip()

pygame.quit()
