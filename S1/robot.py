"""S1."""
import PiBot


class Robot:
    """Class."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.camera = None
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.
        """
        self.robot = robot

    def spin(self):
        """
        The main loop of the robot.

        This loop is expected to call sense, plan, act methods cyclically.
        """
        while not self.shutdown:
            print(f'The time is {self.robot.get_time()}!')
            print(f'{self.camera}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 200:
                self.shutdown = True

    def sense(self):
        """sense."""
        self.camera = self.robot.get_camera_objects()

    def plan(self):
        """plan."""
        if self.robot.get_time < 50.0:
            self.left_wheel_speed = -10
            self.right_wheel_speed = 10
        else:
            self.left_wheel_speed = 0
            self.right_wheel_speed = 0

    def act(self):
        """act."""
        self.robot.set_left_wheel_speed(self.left_wheel_speed)
        self.robot.set_right_wheel_speed(self.right_wheel_speed)
