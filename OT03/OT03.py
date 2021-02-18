"""OT03 - Instantaneous velocity."""
from robot import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.wheel = self.robot.WHEEL_DIAMETER / 2
        self.right = 0
        self.left = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        if self.robot.get_time() != 0:
            return (self.left * 3.14 / 9) * self.wheel
        return 0

    def get_right_velocity(self) -> float:
        """
        Return the current right wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        if self.robot.get_time() != 0:
            return (self.right * 3.14 / 9) * self.wheel
        return 0

    def sense(self):
        """Read the sensor values from the PiBot API."""
        self.right = self.robot.get_right_wheel_encoder()
        self.left = self.robot.get_left_wheel_encoder()

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


if __name__ == "__main__":
    Robot.spin()
