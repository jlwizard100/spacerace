# physics.py

"""
A simple physics module for a 3D space game.
Handles the position, velocity, orientation, and dynamics of a spaceship.
"""

# --- Vector Math Utilities ---

def add_vectors(v1, v2):
    """Adds two 3D vectors."""
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def scale_vector(v, s):
    """Scales a 3D vector by a scalar."""
    return [v[0] * s, v[1] * s, v[2] * s]


class Spaceship:
    """
    Represents a spaceship with Newtonian physics.
    Uses lists of 3 floats for 3D vectors.
    """
    def __init__(self, position=None, velocity=None, orientation=None, mass=1000.0):
        """
        Initializes the spaceship's state.

        :param position: Initial position [x, y, z] in meters.
        :param velocity: Initial velocity [vx, vy, vz] in meters/sec.
        :param orientation: Initial orientation [pitch, yaw, roll] in degrees.
        :param mass: Mass of the ship in kg.
        """
        self.position = position if position is not None else [0.0, 0.0, 0.0]
        self.velocity = velocity if velocity is not None else [0.0, 0.0, 0.0]

        # Orientation as Euler angles (pitch, yaw, roll) in degrees
        self.orientation = orientation if orientation is not None else [0.0, 0.0, 0.0]
        self.angular_velocity = [0.0, 0.0, 0.0]  # In degrees/sec

        self.mass = mass  # in kg

        # For simplicity, we'll use a simplified moment of inertia.
        self.inertia_tensor = [1000.0, 1000.0, 1000.0]

        # We will accumulate forces and torques over a frame before updating.
        self.total_force = [0.0, 0.0, 0.0]
        self.total_torque = [0.0, 0.0, 0.0]

    def __repr__(self):
        return (
            f"Spaceship(pos={self.position}, vel={self.velocity}, "
            f"orient={self.orientation}, ang_vel={self.angular_velocity})"
        )

    def apply_force(self, force):
        """
        Applies a force to the spaceship's center of mass.
        The force is accumulated over a frame.
        :param force: A 3D vector representing the force in Newtons.
        """
        self.total_force = add_vectors(self.total_force, force)

    def apply_torque(self, torque):
        """
        Applies a torque to the spaceship.
        The torque is accumulated over a frame.
        :param torque: A 3D vector representing the torque in Newton-meters.
        """
        self.total_torque = add_vectors(self.total_torque, torque)

    def update(self, delta_time):
        """
        Updates the spaceship's state after a time step.
        This should be called once per frame.
        :param delta_time: The time elapsed since the last frame in seconds.
        """
        # --- Linear Dynamics (Translation) ---
        # Calculate acceleration: a = F / m
        linear_acceleration = scale_vector(self.total_force, 1.0 / self.mass)

        # Update velocity: v = v + a * dt
        self.velocity = add_vectors(self.velocity, scale_vector(linear_acceleration, delta_time))

        # Update position: p = p + v * dt
        self.position = add_vectors(self.position, scale_vector(self.velocity, delta_time))

        # --- Angular Dynamics (Rotation) ---
        # Calculate angular acceleration: alpha = T / I
        # Note: This is a simplified model assuming the inertia tensor is diagonal.
        angular_acceleration = [
            self.total_torque[0] / self.inertia_tensor[0],
            self.total_torque[1] / self.inertia_tensor[1],
            self.total_torque[2] / self.inertia_tensor[2],
        ]

        # Update angular velocity: omega = omega + alpha * dt
        self.angular_velocity = add_vectors(self.angular_velocity, scale_vector(angular_acceleration, delta_time))

        # Update orientation: theta = theta + omega * dt
        self.orientation = add_vectors(self.orientation, scale_vector(self.angular_velocity, delta_time))

        # Reset accumulators for the next frame
        self.total_force = [0.0, 0.0, 0.0]
        self.total_torque = [0.0, 0.0, 0.0]


class Asteroid:
    """
    Represents a single asteroid in the game world. Primarily a data container.
    """
    def __init__(self, model_id, position, orientation, size, angular_velocity):
        self.model_id = model_id
        self.position = position
        self.orientation = orientation  # Stored as a quaternion [w, x, y, z]
        self.size = size
        self.angular_velocity = angular_velocity  # Stored as a vector [x, y, z]

    def __repr__(self):
        return (
            f"Asteroid(model='{self.model_id}', pos={self.position}, size={self.size})"
        )
