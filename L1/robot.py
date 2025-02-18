"""L1."""
import PiBot
import math


class Robot:
    """Robot."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.simulation = self.robot.is_simulation()
        self.wheel_size = self.robot.WHEEL_DIAMETER * math.pi
        self.leftmost_line_sensor = 0
        self.second_left_line_sensor = 0
        self.center_left_line_sensor = 0

        self.rightmost_line_sensor = 0
        self.second_right_line_sensor = 0
        self.center_right_line_sensor = 0
        self.all = []
        self.r_corrector = 0
        self.l_corrector = 0

        self.line_direction = None

        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

        self.state = "Finding the line"
        self.prev_dir = ""
        self.no_line_counter = 0

        self.right_encoder = 0
        self.left_encoder = 0
        self.time = 0

        self.previous_right = 0
        self.previous_left = 0
        self.previous_time = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.
        """
        self.robot = robot

    def find_the_line(self):
        """Instruction for robot to find the line."""
        if self.center_left_line_sensor < 400 and self.center_right_line_sensor < 400:
            print("Line found!")
            self.state = "Following the line"
        elif self.leftmost_line_sensor < 400 or self.second_left_line_sensor < 400:
            self.left_wheel_speed = -8
            self.right_wheel_speed = 8
        else:
            self.left_wheel_speed = 8
            self.right_wheel_speed = -8

    def get_line_direction(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
           right: Line is on the right (i.e., the robot should turn right to reach the line again)
           straight: Robot is on the line (i.e., the robot should not turn to stay on the line)
           left: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        self.prev_dir = self.line_direction
        if self.center_left_line_sensor < 400 and self.center_right_line_sensor < 400:
            self.line_direction = "straight"
        elif self.leftmost_line_sensor < 400 or self.second_left_line_sensor < 400:
            self.line_direction = "left"
        elif self.rightmost_line_sensor < 400 or self.second_right_line_sensor < 400:
            self.line_direction = "right"
        else:
            self.line_direction = "absent"
        return self.line_direction

    def follow_the_line(self):
        """Instruction for robot to follow the line."""
        self.line_direction = self.get_line_direction()
        if self.line_direction == "straight":
            self.moving_straight_correlation()
        elif self.line_direction == "right":
            self.moving_right_correlation()
        elif self.line_direction == "left":
            self.moving_left_correlation()
        elif self.line_direction == "absent":
            self.no_line_counter += 1
            print(f"No line counter = {self.no_line_counter}")

        if self.no_line_counter > 0 and self.line_direction != "absent":
            self.no_line_counter = 0
        elif self.no_line_counter > 50:
            self.shutdown = True

    def moving_straight_correlation(self):
        """Check if velocity of wheels is the same and correlate it."""
        if self.line_direction == self.prev_dir and not self.simulation:
            if self.get_left_velocity() > self.get_right_velocity():
                self.r_corrector += 1
            elif self.get_left_velocity() < self.get_right_velocity():
                self.l_corrector += 1
        self.left_wheel_speed = 10 + self.l_corrector
        self.right_wheel_speed = 10 + self.r_corrector

    def moving_left_correlation(self):
        """Check if turning left is going okay and correlate it."""
        if self.line_direction == self.prev_dir and not self.simulation:
            if self.get_left_velocity() + self.get_right_velocity() > 0:
                self.r_corrector += 1
                self.l_corrector -= 1
        else:
            self.r_corrector = 0
            self.l_corrector = 0
        self.left_wheel_speed = -8 + self.l_corrector
        self.right_wheel_speed = 8 + self.r_corrector

    def moving_right_correlation(self):
        """Check if turning right is going okay and correlate it."""
        if self.line_direction == self.prev_dir and not self.simulation:
            if self.get_left_velocity() + self.get_right_velocity() > 0:
                self.r_corrector -= 1
                self.l_corrector += 1
        else:
            self.r_corrector = 0
            self.l_corrector = 0
        self.left_wheel_speed = 8 + self.l_corrector
        self.right_wheel_speed = -8 + self.r_corrector

    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        velocity = 0
        if self.robot.get_time() != 0:
            velocity = (self.left_encoder - self.previous_left) / 360 * self.wheel_size /\
                       (self.time - self.previous_time)
        return velocity

    def get_right_velocity(self) -> float:
        """
        Return the current right wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        velocity = 0
        if self.robot.get_time() != 0:
            velocity = (self.right_encoder - self.previous_right) / 360 * self.wheel_size / \
                       (self.time - self.previous_time)
        return velocity

    def sense(self):
        """Sense - gets all the information."""
        print("Getting info!")
        self.previous_right = self.right_encoder
        self.previous_left = self.left_encoder
        self.previous_time = self.time

        self.right_encoder = self.robot.get_right_wheel_encoder()
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.time = self.robot.get_time()

        self.leftmost_line_sensor = self.robot.get_leftmost_line_sensor()
        self.second_left_line_sensor = self.robot.get_second_line_sensor_from_left()
        self.center_left_line_sensor = self.robot.get_third_line_sensor_from_left()

        self.rightmost_line_sensor = self.robot.get_rightmost_line_sensor()
        self.second_right_line_sensor = self.robot.get_second_line_sensor_from_right()
        self.center_right_line_sensor = self.robot.get_third_line_sensor_from_right()

        self.all = self.robot.get_left_line_sensors()
        self.all += [self.center_right_line_sensor, self.second_right_line_sensor, self.rightmost_line_sensor]

    def plan(self):
        """Plan - decides what to do based on the information."""
        if self.state == "Finding the line":
            self.find_the_line()
        elif self.state == "Following the line":
            self.follow_the_line()

        if self.shutdown:
            self.left_wheel_speed = 0
            self.right_wheel_speed = 0

    def act(self):
        """Act - does stuff based on the decision made."""
        self.robot.set_left_wheel_speed(self.left_wheel_speed)
        self.robot.set_right_wheel_speed(self.right_wheel_speed)

    def spin(self):
        """
        The main loop of the robot.

        This loop is expected to call sense, plan, act methods cyclically.
        """
        while not self.shutdown:
            print(f'The time is {self.robot.get_time()}!')
            self.sense()
            print(f"Left sensor: {self.center_left_line_sensor}, Right sensor: {self.center_right_line_sensor}")
            print(f"{self.all}")
            self.plan()
            self.act()
            self.robot.sleep(0.05)
            if self.robot.get_time() > 2000:
                self.shutdown = True


def main():
    """
    The main function.

    Create a Robot class object and run it.
    """
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
