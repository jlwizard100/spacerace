import configparser

class SpaceracerConfig:
    def __init__(self, filepath):
        self.config = configparser.ConfigParser()
        self.filepath = filepath
        self.is_open = False

    def open(self):
        """Opens and reads the configuration file."""
        if not self.is_open:
            self.config.read(self.filepath)
            self.is_open = True

    def close(self):
        """Closes the configuration file (metaphorically)."""
        self.is_open = False
        # configparser doesn't keep the file open, so this is more for state management.
        # If we were writing, we'd save changes here.

    def get_value(self, section, key):
        """Returns a specific value from the configuration file."""
        if not self.is_open:
            raise ValueError("Configuration file is not open. Call 'open()' first.")
        return self.config.get(section, key)

    def get_section(self, section):
        """Returns a dictionary of all key-value pairs in a section."""
        if not self.is_open:
            raise ValueError("Configuration file is not open. Call 'open()' first.")
        return dict(self.config.items(section))
