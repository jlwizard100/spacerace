import configparser

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
    Main function to load and print the configuration.
    """
    try:
        settings = load_configuration()

        print("--- Spacerace Configuration Loaded ---")
        for section, key in settings.items():
            print(f"{section.replace('_', ' ').title()}: {key}")

        print("\n--- Example Usage in Your Game ---")
        print("You can now use the 'settings' dictionary to configure your game.")
        print("For example, to set up the display:")

        if settings['fullscreen']:
            print(f"Setting fullscreen mode: {settings['screen_width']}x{settings['screen_height']}")
            # In your actual game, you would call your graphics engine's function here, e.g.:
            # graphics.set_mode(settings['screen_width'], settings['screen_height'], fullscreen=True)
        else:
            print(f"Setting windowed mode: {settings['screen_width']}x{settings['screen_height']}")
            # graphics.set_mode(settings['screen_width'], settings['screen_height'], fullscreen=False)

    except FileNotFoundError:
        print("Error: config.ini not found. Make sure the file exists in the same directory.")
    except configparser.Error as e:
        print(f"Error parsing config.ini: {e}")


if __name__ == "__main__":
    main()
