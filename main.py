import pygame
import configparser
import json
import ast
import numpy as np
from physics import Spaceship
from game_objects import Asteroid, Gate, load_course_from_file
from renderer import Camera, draw_ship, draw_asteroid, draw_gate

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
COLOR_BACKGROUND = (10, 10, 20)
COLOR_TEXT = (220, 220, 220)

# --- Helper functions ---
def draw_text(surface, text, pos, font, color=COLOR_TEXT):
    """Generic text drawing function."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)
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
        # Joystick Settings
        'joystick_id': config.getint('Joystick', 'joystick_id', fallback=0),
        'invert_pitch': config.getboolean('Joystick', 'invert_pitch', fallback=True),
        'deadzone': config.getfloat('Joystick', 'deadzone', fallback=0.1),
        'axis_yaw': config.getint('Joystick', 'axis_yaw', fallback=2),
        'axis_pitch': config.getint('Joystick', 'axis_pitch', fallback=1),
        'axis_roll': config.getint('Joystick', 'axis_roll', fallback=0),
        'axis_thrust': config.getint('Joystick', 'axis_thrust', fallback=3),
    }
    return settings

def reset_game_state(ship, scene_gates, settings):
    """Resets the ship and game progress."""
    # This print will go to the console, which is fine for a reset event.
    print("INFO: Resetting game state.")
    ship.position = np.array(settings.get('starting_vector'), dtype=float)
    ship.velocity = np.array([0.0, 0.0, 0.0])
    ship.orientation = np.array([1.0, 0.0, 0.0, 0.0])
    ship.angular_velocity = np.array([0.0, 0.0, 0.0])
    for gate in scene_gates:
        gate.is_passed = False
    return 0, False # current_gate_index, game_over

def main():
    # --- Initialization ---
    settings = load_configuration()

    pygame.init()

    # --- Joystick Initialization ---
    joystick = None
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick_id = settings.get('joystick_id', 0)
        if joystick_id < pygame.joystick.get_count():
            joystick = pygame.joystick.Joystick(joystick_id)
            joystick.init()
            print(f"INFO: Enabled joystick: {joystick.get_name()}")
        else:
            print(f"WARN: Joystick ID {joystick_id} not found.")

    screen_width = settings.get('screen_width')
    screen_height = settings.get('screen_height')
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Spacerace")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # --- Load Game Objects ---
    scene_asteroids = []
    scene_gates = []
    try:
        course_data = load_course_from_file("course.json")
        scene_asteroids = course_data.get("asteroids", [])
        scene_gates = course_data.get("gates", [])
        print(f"Successfully loaded {len(scene_asteroids)} asteroids and {len(scene_gates)} gates.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load course.json: {e}. Starting with an empty course.")

    ship = Spaceship(
        mass=settings.get('ship_weight'),
        position=settings.get('starting_vector')
    )

    camera = Camera(screen_width, screen_height)

    # --- Game State ---
    current_gate_index, game_over = reset_game_state(ship, scene_gates, settings)

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
                if event.key == pygame.K_r:
                    current_gate_index, game_over = reset_game_state(ship, scene_gates, settings)

        dt = clock.tick(60) / 1000.0

        # --- Game Logic ---
        if not game_over:
            # Input handling
            keys = pygame.key.get_pressed()
            main_thrust = settings.get('max_forward_thruster', 50000)
            steer_torque_strength = main_thrust * 0.05

            if keys[pygame.K_w]: ship.apply_force(np.array([0, 0, main_thrust]), local_space=True)
            if keys[pygame.K_s]: ship.apply_force(np.array([0, 0, -main_thrust * 0.5]), local_space=True)
            if keys[pygame.K_d]: ship.apply_torque(np.array([0, -steer_torque_strength, 0]))
            if keys[pygame.K_a]: ship.apply_torque(np.array([0, steer_torque_strength, 0]))
            if keys[pygame.K_e]: ship.apply_torque(np.array([0, 0, -steer_torque_strength * 0.5]))
            if keys[pygame.K_q]: ship.apply_torque(np.array([0, 0, steer_torque_strength * 0.5]))
            if keys[pygame.K_UP]: ship.apply_torque(np.array([-steer_torque_strength, 0, 0]))
            if keys[pygame.K_DOWN]: ship.apply_torque(np.array([steer_torque_strength, 0, 0]))

            # Joystick input handling
            if joystick:
                deadzone = settings.get('deadzone')
                yaw_in = joystick.get_axis(settings.get('axis_yaw'))
                if abs(yaw_in) > deadzone: ship.apply_torque(np.array([0, -yaw_in * steer_torque_strength, 0]))
                pitch_in = joystick.get_axis(settings.get('axis_pitch'))
                if abs(pitch_in) > deadzone:
                    pitch_val = -pitch_in if settings.get('invert_pitch') else pitch_in
                    ship.apply_torque(np.array([pitch_val * steer_torque_strength, 0, 0]))
                roll_in = joystick.get_axis(settings.get('axis_roll'))
                if abs(roll_in) > deadzone: ship.apply_torque(np.array([0, 0, -roll_in * steer_torque_strength * 0.5]))
                thrust_in = -joystick.get_axis(settings.get('axis_thrust'))
                if thrust_in > deadzone:
                    thrust_power = (thrust_in - deadzone) / (1 - deadzone)
                    ship.apply_force(np.array([0, 0, thrust_power * main_thrust]), local_space=True)

            ship.update(dt)

            if current_gate_index < len(scene_gates):
                target_gate = scene_gates[current_gate_index]
                if np.linalg.norm(ship.position - target_gate.position) < target_gate.size:
                    print(f"INFO: Passed gate {current_gate_index + 1}!")
                    target_gate.is_passed = True
                    current_gate_index += 1

            ship_radius = 15
            for asteroid in scene_asteroids:
                if np.linalg.norm(ship.position - asteroid.position) < (asteroid.size / 2 + ship_radius):
                    print("EVENT: Ship crashed into an asteroid! GAME OVER.")
                    game_over = True
                    break

        camera.update(ship)

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)

        for i, gate in enumerate(scene_gates):
            gate.is_next = (i == current_gate_index)
            draw_gate(screen, gate, camera)
        for asteroid in scene_asteroids:
            draw_asteroid(screen, asteroid, camera)
        draw_ship(screen, ship, camera)

        # HUD
        if game_over:
            hud_text = "GAME OVER - Press 'R' to Restart"
        elif current_gate_index >= len(scene_gates):
            hud_text = "Finish!"
        else:
            hud_text = f"Next Gate: {current_gate_index + 1} / {len(scene_gates)}"
        draw_text(screen, hud_text, (10, 10), font)

        if np.linalg.norm(ship.velocity) > 1.0:
            vel_right = np.dot(ship.velocity, ship.get_right_vector())
            vel_up = np.dot(ship.velocity, ship.get_up_vector())
            vel_dir_2d = np.array([vel_right, vel_up])
            if np.linalg.norm(vel_dir_2d) > 1.0:
                vel_dir_2d /= np.linalg.norm(vel_dir_2d)
                center_x, center_y = screen_width / 2, screen_height / 2
                end_pos = (center_x + vel_dir_2d[0] * 50, center_y - vel_dir_2d[1] * 50)
                pygame.draw.line(screen, (255, 255, 0), (center_x, center_y), end_pos, 2)

        pygame.display.flip()

    pygame.quit()
    print("--- Game loop exited. ---")

if __name__ == "__main__":
    main()
