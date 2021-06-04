"""OT17 - Mapping with a laser sensor."""
import PiBot
import math


class Robot:
    """The robot class."""

    def __init__(self, initial_odom: list = [0, 0, 0],
                 cell_size: float = 0.3, heading_tolerance: float = 5):
        """
        Initialize variables.

        Arguments:
          initial_odom -- Initial odometry, [x, y, yaw] in
            [meters, meters, radians]
          cell_size -- cell edge length in meters
          heading_tolerance -- the number of degrees
            deviation (+/-) allowed for direction classification
        """
        self.robot = PiBot.PiBot()
        if initial_odom is None:
            initial_odom = [0, 0, 0]
        self.robot = PiBot.PiBot()
        self.cell_size = cell_size
        self.heading_tolerance = heading_tolerance

        self.x_pos = initial_odom[0]
        self.y_pos = initial_odom[1]
        self.yaw = initial_odom[2]

        self.right_wheel_encoder_now = 0
        self.right_wheel_encoder_last = 0
        self.left_wheel_encoder_now = 0
        self.left_wheel_encoder_last = 0

        self.current_time = 0
        self.previous_time = 0

        self.laser = 0

        self.sensed = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set PiBot reference."""
        self.robot = robot

    def sense(self):
        """SPA architecture sense method."""
        self.sensed = True

        self.laser = self.robot.get_front_middle_laser()

        self.left_wheel_encoder_last = self.left_wheel_encoder_now
        self.right_wheel_encoder_last = self.right_wheel_encoder_now
        self.left_wheel_encoder_now = self.robot.get_left_wheel_encoder()
        self.right_wheel_encoder_now = self.robot.get_right_wheel_encoder()

        self.previous_time = self.current_time
        self.current_time = self.robot.get_time()

        self.yaw = math.degrees(self.robot.get_rotation()) % 360

    def update_pose(self) -> None:
        """Update the robot pose."""
        radius = self.robot.WHEEL_DIAMETER / 2
        angular_left = (math.radians(self.left_wheel_encoder_now - self.left_wheel_encoder_last))
        angular_right = (math.radians(self.right_wheel_encoder_now - self.right_wheel_encoder_last))

        ride = (angular_left + angular_right) / 2
        self.x_pos += radius * ride * math.cos(math.radians(self.yaw))
        self.y_pos += radius * ride * math.sin(math.radians(self.yaw))

    def update_map(self) -> None:
        """Update map based on the current pose and the laser reading."""
        # Your code here...
        pass

    def get_map(self) -> str:
        """
        Print the known map.

        Returns:
          If the map is empty, must return None.
          The string representation of the map.
          Each cell should be one character + all neighboring cells/walls.
          The unknown spaces and walls should be denoted as "?"
          The walls should be marked as "X"

          An example:
            ?X?X???
            X   X??
            ? ? ?X?
            ? X   X
            ? ?X? ?
            ? X   X
            ? ? ?X?
            X   X??
            ?X?X???
        """
        if self.laser is None:
            return None
        return "            ?X?X???" \
               "X   X??" \
               "? ? ?X?" \
               "? X   X" \
               "? ?X? ?" \
               "? X   X" \
               "? ? ?X?" \
               "X   X??" \
               "?X?X???"

    def spin(self):
        """The main loop."""
        for _ in range(10):
            self.sense()
            self.update_pose()
            self.update_map()
            self.robot.sleep(0.05)
        print(f"{self.get_map()}")


def main():
    """The main entry point."""
    robot = Robot(initial_odom=[0.16, 2.262, -1.57],
                  cell_size=0.3, heading_tolerance=5)
    robot.spin()


def test():
    robot = Robot()
    import m1 # or any other data file
    data = m1.get_data()
    robot.robot.load_data_profile(data)
    for i in range(len(data)):
        print(f"laser = {robot.robot.get_front_middle_laser()}")
        robot.robot.sleep(0.05)


if __name__ == "__main__":
    test()
