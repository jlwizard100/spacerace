import configparser
import json
import ast
from physics import Spaceship, Asteroid
import time

# This script demonstrates how to read the settings from config.ini.
# You can adapt this code to load the configuration in your game.

def _parse_value_with_units(value_str):
    """
    Strips common units ('kg', 'm') from a string and returns the numerical part.
    Returns an int or float.
    """
    s = value_str.lower().strip().replace("kg", "").replace("m", "")
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        # Return 0 or raise an error if parsing fails
        return 0

def load_configuration():
    """
    Loads and parses the configuration from config.ini.
    Returns a dictionary with the game settings.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    settings = {
        # Player Settings
        'player_name': config.get('Player', 'name'),

        # Graphics Settings
        'screen_width': config.getint('Graphics', 'screen_width'),
        'screen_height': config.getint('Graphics', 'screen_height'),
        'fullscreen': config.getboolean('Graphics', 'fullscreen'),
        'fov': config.getint('Graphics', 'fov'),

        # ShipConfig Settings
        'ship_weight': _parse_value_with_units(config.get('ShipConfig', 'Ship_weight')),
        'ship_length': _parse_value_with_units(config.get('ShipConfig', 'Ship_length')),
        'ship_width': _parse_value_with_units(config.get('ShipConfig', 'Ship_width')),
        'starting_vector': list(ast.literal_eval(config.get('ShipConfig', 'Starting_vector'))),

        # Game Settings
        'mouse_sensitivity': config.getfloat('Game', 'mouse_sensitivity'),
        'invert_y_axis': config.getboolean('Game', 'invert_y_axis'),

        # Physics Settings
        'gravity_enabled': config.getboolean('Physics', 'gravity_enabled'),
        'max_forward_thruster': config.getint('Physics', 'Max_forward_thruster'),
        'max_reverse_thruster': config.getint('Physics', 'Max_reverse_thruster'),
        'max_steering_thruster': config.getint('Physics', 'Max_steering_thruster'),

        # Joystick Settings
        'joystick_id': config.getint('Joystick', 'joystick_id'),
        'invert_pitch': config.getboolean('Joystick', 'invert_pitch'),
        'deadzone': config.getfloat('Joystick', 'deadzone'),
        'axis_yaw': config.getint('Joystick', 'axis_yaw'),
        'axis_pitch': config.getint('Joystick', 'axis_pitch'),
        'axis_roll': config.getint('Joystick', 'axis_roll'),
        'axis_thrust': config.getint('Joystick', 'axis_thrust'),
    }
    return settings

def main():
    """
    Main function to load configuration and demonstrate the physics module.
    """
    try:
        settings = load_configuration()
        print("--- Spacerace Configuration Loaded ---")
        # You can still use the settings dictionary for game setup.
        # For example: ship_mass = settings.get('mass', 1000)

    except (FileNotFoundError, configparser.Error) as e:
        print(f"Could not load or parse config.ini: {e}")
        print("Using default values for demonstration.")

    # Load the course from course.json
    asteroids_data = []
    try:
        with open("course.json", 'r') as f:
            course_data = json.load(f)
            asteroids_data = course_data.get("asteroids", [])
            print(f"--- Loaded course '{course_data.get('course_name')}' with {len(asteroids_data)} asteroids ---")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not load or parse course.json: {e}")
        print("Proceeding without any asteroids.")

    # Create Asteroid objects from the loaded data
    scene_asteroids = [
        Asteroid(
            model_id=data.get('model_id'),
            position=data.get('position'),
            orientation=data.get('orientation'),
            size=data.get('size'),
            angular_velocity=data.get('angular_velocity')
        )
        for data in asteroids_data
    ]
    if scene_asteroids:
        print(f"--- Created {len(scene_asteroids)} asteroid objects from course data. ---")

    print("\n--- Physics Module Demonstration ---")

    # 1. Create a spaceship instance using settings from config.ini
    ship = Spaceship(
        mass=settings.get('ship_weight', 1000),
        position=settings.get('starting_vector', [0.0, 0.0, 0.0])
    )
    print(f"Initial state: {ship}")

    # 2. Define simulation parameters
    simulation_duration = 5  # seconds
    delta_time = 1.0         # second per step
    steps = int(simulation_duration / delta_time)

    # 3. Define forces and torques to apply from config settings
    forward_thrust = [settings.get('max_forward_thruster', 1000), 0, 0]
    # For demonstration, we'll still use a hardcoded yaw torque
    yaw_torque = [0, 0, 500]       # 500 Nm of torque around the Z-axis (yaw)

    # 4. Run the simulation loop
    for i in range(steps):
        print(f"\n--- Step {i+1} (Time: {(i+1)*delta_time:.1f}s) ---")

        # Apply forces and torques every frame
        ship.apply_force(forward_thrust)
        ship.apply_torque(yaw_torque)

        # Update the physics simulation
        ship.update(delta_time)

        # Print the new state
        # Using repr for a compact view of the state
        print(f"New state: {ship}")


if __name__ == "__main__":
    main()
