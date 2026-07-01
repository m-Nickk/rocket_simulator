import random
import pygame
import math

# Initialize Pygame modules
pygame.init()

# Template class for the rocket behavior and physics
class Rocket:
    def __init__(self, name, x, y, m0, mf, isp, color, mkg, current_mass, speed=0, g = 10, altitude = 0):
        self.name = name
        self.x = x
        self.y = y
        self.m0 = m0
        self.mf = mf
        self.isp = isp
        self.color = color
        self.mkg = mkg
        self.speed = speed
        self.current_mass = current_mass
        self.g = g
        self.engine_on = False
        self.altitude = altitude
    
    def update(self, dt):

        thrust = 0

        # Calculate thrust if engine is active and fuel is available
        if self.engine_on and self.current_mass > self.mf:
            self.current_mass -= self.mkg * dt
            thrust = self.mkg * self.isp * self.g

        # Apply gravitational force and calculate acceleration
        gravity = self.current_mass * self.g
        acceleration = (thrust - gravity) / self.current_mass 

        # Update flight speed based on acceleration
        self.speed += acceleration * dt

        # Update current altitude based on speed
        self.altitude += self.speed * dt

        # Handle ground collision physics
        if self.altitude <= 0 and self.speed < 0:
            self.altitude = 0
            self.speed = 0
            self.engine_on = False
    
# Create the first rocket instance
rocket_1 = Rocket("Rocket_1", x=440, y=600, m0=500, mf=100, isp=400, color=(200, 200, 200), mkg=15, current_mass = 500)

### Soon ### remaining_fuel = (rocket_1.current_mass - rocket_1.mf) / (rocket_1.m0 - rocket_1.mf)

# Set up the game window resolution
screen = pygame.display.set_mode((900, 900))

# Initialize font system and create font style
pygame.font.init()
font = pygame.font.SysFont("Arial", 16, bold=True)

# Set up time tracking and default delta time
clock = pygame.time.Clock()
dt = 0.016

# Main game loop flag
running = True

# Generate background stars
stars = []
for i in range(100):
    star_x = random.randint(0, 900)
    star_y = random.randint(0, 900)
    stars.append( [star_x, star_y])

# Start of the main application loop
while running:

    # Calculate delta time based on 60 FPS target
    dt = clock.tick(60) / 1000.0
    
    # Process user input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle rocket engine state
                rocket_1.engine_on = not rocket_1.engine_on
    
    # Clear the screen
    screen.fill((0, 0, 0))

    # Move and render stars to simulate flight speed
    for star in stars:
        star[1] += rocket_1.speed * dt * 0.5

        # Reset star position if it goes off the screen
        if star[1] > 900:
            star[1] = 0
            star[0] = random.randint(0, 900)

        pygame.draw.circle(screen, (255, 255, 255), (int(star[0]), int(star[1])), 2)

    # Draw the rocket
    pygame.draw.rect(screen, rocket_1.color, (int(rocket_1.x), int(rocket_1.y), 20, 50))
    # Update rocket physics state
    rocket_1.update(dt)

    # Render telemetry text labels
    text_mass = font.render(f"Mass: {int(rocket_1.current_mass)} kg", True, (255, 255, 255))
    text_speed = font.render(f"Speed: {int(rocket_1.speed)} m/s", True, (255, 255, 255))
    text_altitude = font.render(f"Altitude: {int(rocket_1.altitude)} meters", True, (255, 255, 255))

    # Draw text
    screen.blit(text_mass, (10, 10))
    screen.blit(text_speed, (10, 30))
    screen.blit(text_altitude, (10, 50))

    # Swap buffers to display the rendered frame
    pygame.display.flip()