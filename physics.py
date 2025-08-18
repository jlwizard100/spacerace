import numpy as np
from utils import qv_rotate, q_multiply

class Spaceship:
    """
    Represents a spaceship with Newtonian physics, using numpy and quaternions.
    """
    def __init__(self, position=None, velocity=None, mass=1000.0):
        """
        Initializes the spaceship's state.
        :param position: Initial position [x, y, z].
        :param velocity: Initial velocity [vx, vy, vz].
        :param mass: Mass of the ship in kg.
        """
        self.position = np.array(position, dtype=float) if position is not None else np.array([0.0, 0.0, 0.0])
        self.velocity = np.array(velocity, dtype=float) if velocity is not None else np.array([0.0, 0.0, 0.0])

        # Orientation as a quaternion [w, x, y, z]
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])
        self.angular_velocity = np.array([0.0, 0.0, 0.0]) # In radians/sec

        self.mass = mass
        # Simplified moment of inertia tensor (assumes symmetry)
        self.inertia_tensor = np.array([15000.0, 15000.0, 5000.0])

        # Accumulators for forces and torques applied over a frame
        self.total_force = np.array([0.0, 0.0, 0.0])
        self.total_torque = np.array([0.0, 0.0, 0.0])

    def __repr__(self):
        return (f"Spaceship(pos={self.position.round(1)}, vel={self.velocity.round(1)})")

    def get_forward_vector(self):
        """Returns the vector pointing in the ship's forward direction."""
        return qv_rotate(self.orientation, np.array([0, 0, 1]))

    def get_up_vector(self):
        """Returns the vector pointing in the ship's up direction."""
        return qv_rotate(self.orientation, np.array([0, 1, 0]))

    def get_right_vector(self):
        """Returns the vector pointing in the ship's right direction."""
        return qv_rotate(self.orientation, np.array([1, 0, 0]))

    def apply_force(self, force, local_space=False):
        """
        Applies a force. If local_space is True, the force is relative
        to the ship's orientation.
        """
        if local_space:
            force = qv_rotate(self.orientation, force)
        self.total_force += force

    def apply_torque(self, torque):
        """Applies a torque to the spaceship."""
        self.total_torque += torque

    def update(self, delta_time):
        """Updates the spaceship's state after a time step."""
        # --- Linear Dynamics ---
        linear_acceleration = self.total_force / self.mass
        self.velocity += linear_acceleration * delta_time
        self.position += self.velocity * delta_time

        # --- Angular Dynamics (using quaternion kinematics) ---
        angular_acceleration = self.total_torque / self.inertia_tensor
        self.angular_velocity += angular_acceleration * delta_time

        # Update orientation quaternion from angular velocity
        # Create a "pure" quaternion from the angular velocity vector
        w_quat = np.concatenate(([0.0], self.angular_velocity))
        # Calculate the rate of change of the orientation quaternion
        q_derivative = 0.5 * q_multiply(self.orientation, w_quat)
        # Update the orientation
        self.orientation += q_derivative * delta_time
        # Re-normalize the quaternion to prevent floating point drift
        self.orientation /= np.linalg.norm(self.orientation)

        # Reset accumulators for the next frame
        self.total_force = np.array([0.0, 0.0, 0.0])
        self.total_torque = np.array([0.0, 0.0, 0.0])
