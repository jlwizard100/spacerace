import configparser
from physics import Spaceship
import time

# This script demonstrates how to read the settings from config.ini.
# You can adapt this code to load the configuration in your game.

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

        # Game Settings
        'mouse_sensitivity': config.getfloat('Game', 'mouse_sensitivity'),
        'invert_y_axis': config.getboolean('Game', 'invert_y_axis'),

        # Physics Settings
        'gravity_enabled': config.getboolean('Physics', 'gravity_enabled'),
        'max_velocity': config.getint('Physics', 'max_velocity'),

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

    print("\n--- Physics Module Demonstration ---")

    # 1. Create a spaceship instance
    ship = Spaceship(mass=1000) # 1000 kg
    print(f"Initial state: {ship}")

    # 2. Define simulation parameters
    simulation_duration = 5  # seconds
    delta_time = 1.0         # second per step
    steps = int(simulation_duration / delta_time)

    # 3. Define forces and torques to apply
    forward_thrust = [1000, 0, 0] # 1000 Newtons of force along the X-axis
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
