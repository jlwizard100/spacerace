import pygame
import configparser
import json
import ast
import numpy as np
from physics import Spaceship
from game_objects import Asteroid, Gate, load_course_from_file
from renderer import Camera, draw_ship, draw_asteroid

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
COLOR_BACKGROUND = (10, 10, 20)

# --- Helper functions ---
def _parse_value_with_units(value_str):
    """Strips common units and converts to a number."""
    s = value_str.lower().strip().replace("kg", "").replace("m", "")
    try:
        if '.' in s: return float(s)
        return int(s)
    except (ValueError, TypeError): return 0

def load_configuration():
    """Loads and parses the configuration from config.ini, with fallbacks."""
    config = configparser.ConfigParser()
    # Provide default values for robustness
    config.read_dict({
        'Player': {'name': 'Pilot'},
        'Graphics': {'screen_width': str(WIDTH), 'screen_height': str(HEIGHT), 'fullscreen': 'false'},
        'ShipConfig': {'Ship_weight': '1000kg', 'Starting_vector': '(0,0,0)'},
        'Physics': {'Max_forward_thruster': '10000'}
    })
    config.read('config.ini')

    settings = {
        'player_name': config.get('Player', 'name'),
        'screen_width': config.getint('Graphics', 'screen_width'),
        'screen_height': config.getint('Graphics', 'screen_height'),
        'fullscreen': config.getboolean('Graphics', 'fullscreen'),
        'ship_weight': _parse_value_with_units(config.get('ShipConfig', 'Ship_weight')),
        'starting_vector': list(ast.literal_eval(config.get('ShipConfig', 'Starting_vector'))),
        'max_forward_thruster': config.getint('Physics', 'Max_forward_thruster'),
    }
    return settings

def main():
    # --- Initialization ---
    settings = load_configuration()

    pygame.init()
    screen_width = settings.get('screen_width')
    screen_height = settings.get('screen_height')
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Spacerace")
    clock = pygame.time.Clock()

    # --- Load Game Objects ---
    try:
        course_data = load_course_from_file("course.json")
        scene_asteroids = course_data.get("asteroids", [])
        print(f"Successfully loaded {len(scene_asteroids)} asteroids.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load course.json: {e}. Starting with no asteroids.")
        scene_asteroids = []

    ship = Spaceship(
        mass=settings.get('ship_weight'),
        position=settings.get('starting_vector')
    )

    camera = Camera(screen_width, screen_height)

    # --- Main Game Loop ---
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Get delta time in seconds
        dt = clock.tick(60) / 1000.0

        # --- Game Logic ---
        # Input handling
        keys = pygame.key.get_pressed()

        # Define thruster strengths
        main_thrust = settings.get('max_forward_thruster', 50000)
        # Using a fraction of main thrust for steering, can be tuned
        steer_torque_strength = main_thrust * 0.05

        # Apply forces and torques based on input (in local ship space)
        if keys[pygame.K_w]:
            ship.apply_force(np.array([0, 0, main_thrust]), local_space=True)
        if keys[pygame.K_s]:
            ship.apply_force(np.array([0, 0, -main_thrust * 0.5]), local_space=True)

        # Yaw (turn left/right on local Y axis)
        if keys[pygame.K_d]:
            ship.apply_torque(np.array([0, -steer_torque_strength, 0]))
        if keys[pygame.K_a]:
            ship.apply_torque(np.array([0, steer_torque_strength, 0]))

        # Roll (q/e on local Z axis)
        if keys[pygame.K_e]:
            ship.apply_torque(np.array([0, 0, -steer_torque_strength * 0.5]))
        if keys[pygame.K_q]:
            ship.apply_torque(np.array([0, 0, steer_torque_strength * 0.5]))

        # Update physics
        ship.update(dt)
        camera.update(ship)

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)

        # Draw all the asteroids
        for asteroid in scene_asteroids:
            draw_asteroid(screen, asteroid, camera)

        # Draw the ship
        draw_ship(screen, ship, camera)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
