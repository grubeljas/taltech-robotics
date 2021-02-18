"""OT03 - Instantaneous velocity."""
import PiBot
import math


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        self.wheel_size = self.robot.WHEEL_DIAMETER * math.pi

        self.right = 0
        self.left = 0
        self.time = 0

        self.previous_right = 0
        self.previous_left = 0
        self.previous_time = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        velocity = 0
        if self.robot.get_time() != 0:
            velocity = (self.left - self.previous_left) / 360 * self.wheel_size / (self.time - self.previous_time)
        return velocity

    def get_right_velocity(self) -> float:
        """
        Return the current right wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        velocity = 0
        if self.robot.get_time() != 0:
            velocity = (self.right - self.previous_right) / 360 * self.wheel_size / (self.time - self.previous_time)
        return velocity

    def sense(self):
        """Read the sensor values from the PiBot API."""
        self.previous_right = self.right
        self.previous_left = self.left
        self.previous_time = self.time

        self.right = self.robot.get_right_wheel_encoder()
        self.left = self.robot.get_left_wheel_encoder()
        self.time = self.robot.get_time()

    def spin(self):
        """Main loop."""
        while not self.shutdown:
            self.sense()
            timestamp = self.robot.get_time()
            left_velocity = self.get_left_velocity()
            right_velocity = self.get_right_velocity()
            print(f'{timestamp}: {left_velocity} {right_velocity}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def main():
    """Main entry."""
    robot = Robot()
    robot.spin()


def test():
    """Test entry."""
    robot = Robot()
    import constant_slow  # or any other data file
    data = constant_slow.get_data()
    robot.robot.load_velocity_profile(data)
    for i in range(100):
        print(f"left_encoder = {robot.robot.get_left_wheel_encoder()}")
        robot.sense()
        print(f"Left speed = {robot.get_left_velocity()}")
        robot.robot.sleep(0.05)


if __name__ == "__main__":
    test()
