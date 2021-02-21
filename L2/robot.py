"""L2."""
import PiBot


class Robot:
    """Robot."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        self.leftmost_line_sensor = 0
        self.second_left_line_sensor = 0
        self.center_left_line_sensor = 0

        self.rightmost_line_sensor = 0
        self.second_right_line_sensor = 0
        self.center_right_line_sensor = 0

        self.crossroad_turn = "left"
        self.starting_orientation = None
        self.current_orientation = None

        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

        self.state = "Finding the line"
        self.no_line_counter = 0
        self.crossed_line_on_left = False
        self.crossed_line_on_right = False
        self.straight_counter = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.
        """
        self.robot = robot

    def turn_left(self):
        """Robot turns left."""
        self.left_wheel_speed = -8
        self.right_wheel_speed = 8

    def turn_right(self):
        """Robot turns right."""
        self.left_wheel_speed = 8
        self.right_wheel_speed = -8

    def go_straight(self):
        """Robot goes straight."""
        self.left_wheel_speed = 8
        self.right_wheel_speed = 8

    def gradual_turn_left(self):
        """Robot gradually turns left."""
        self.left_wheel_speed = 0
        self.right_wheel_speed = 8

    def gradual_turn_right(self):
        """Robot gradually turns right."""
        self.left_wheel_speed = 8
        self.right_wheel_speed = 0

    def find_the_line(self):
        """Instruction for robot to find the line."""
        if self.center_left_line_sensor < 400 and self.center_right_line_sensor < 400:
            print("Line found!")
            self.state = "Following the line"
        elif self.rightmost_line_sensor < 400 or self.second_right_line_sensor < 400:
            self.turn_right()
        else:
            self.turn_left()

    def find_the_crossroads(self):
        """Instruction for robot to find a crossroad."""
        return self.get_line_direction() == "straight" and \
            (self.rightmost_line_sensor < 200 or self.leftmost_line_sensor < 200) or \
            self.rightmost_line_sensor < 200 and self.leftmost_line_sensor < 200

    def get_line_direction(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
           right: Line is on the right (i.e., the robot should turn right to reach the line again)
           straight: Robot is on the line (i.e., the robot should not turn to stay on the line)
           left: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        line_direction = "absent"

        if self.center_left_line_sensor < 200 and self.center_right_line_sensor < 200:
            line_direction = "straight"
        elif self.second_right_line_sensor < 200 or self.center_right_line_sensor < 200:
            line_direction = "leaning right"
        elif self.second_left_line_sensor < 200 or self.center_left_line_sensor < 200:
            line_direction = "leaning left"
        elif self.rightmost_line_sensor < 200:
            line_direction = "hard right"
        elif self.leftmost_line_sensor < 200:
            line_direction = "hard left"

        return line_direction

    def follow_the_line(self):
        """Instruction for robot to follow the line."""
        line_direction = self.get_line_direction()

        if line_direction == "straight":
            self.go_straight()
        if line_direction == "leaning right":
            self.gradual_turn_right()
        if line_direction == "leaning left":
            self.gradual_turn_left()
        if line_direction == "hard right":
            self.turn_right()
        if line_direction == "hard left":
            self.turn_left()

        if line_direction == "absent":
            self.no_line_counter += 1
        else:
            self.no_line_counter = 0

        if self.no_line_counter > 500:
            self.state = "Finding the line"

        if self.find_the_crossroads():
            self.state = "On a crossroad"
            print(f"On a crossroad, go {self.crossroad_turn}")
            self.starting_orientation = self.current_orientation

    def turn_on_crossroad(self):
        """Instruction for robot to turn on a crossroad."""
        current_turn_angle = 0
        line_direction = self.get_line_direction()
        if self.rightmost_line_sensor < 200:
            self.crossed_line_on_right = True
        if self.leftmost_line_sensor < 200:
            self.crossed_line_on_left = True

        if self.crossroad_turn == "left":
            self.gradual_turn_left()
            if line_direction == "absent":
                self.turn_left()
            current_turn_angle = abs(self.current_orientation - self.starting_orientation)

        if self.crossroad_turn == "right":
            self.gradual_turn_right()
            if line_direction == "absent":
                self.turn_right()
            current_turn_angle = abs(self.current_orientation - self.starting_orientation)

        if self.crossroad_turn == "straight":
            self.go_straight()
            self.straight_counter += 1

        self.turn_on_crossroads2(line_direction, current_turn_angle)

    def turn_on_crossroads2(self, line_direction, angle):
        if self.crossroad_turn == "straight" and self.crossed_line_on_right and self.crossed_line_on_left and \
                self.straight_counter > 30:
            self.crossroad_turn = "right"
            self.state = "Following the line"
            self.straight_counter = 0
        elif line_direction == "straight" and angle > 40:
            self.state = "Following the line"
            if self.crossroad_turn == "left":
                self.crossroad_turn = "straight"
            else:
                self.crossroad_turn = "left"

    def sense(self):
        """Sense - gets all the information."""
        self.leftmost_line_sensor = self.robot.get_leftmost_line_sensor()
        self.second_left_line_sensor = self.robot.get_second_line_sensor_from_left()
        self.center_left_line_sensor = self.robot.get_third_line_sensor_from_left()

        self.rightmost_line_sensor = self.robot.get_rightmost_line_sensor()
        self.second_right_line_sensor = self.robot.get_second_line_sensor_from_right()
        self.center_right_line_sensor = self.robot.get_third_line_sensor_from_right()

        self.current_orientation = self.robot.get_rotation()

    def plan(self):
        """Plan - decides what to do based on the information."""
        if self.state == "Finding the line":
            self.find_the_line()
        elif self.state == "Following the line":
            self.follow_the_line()
        elif self.state == "On a crossroad":
            self.turn_on_crossroad()

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
            #  print(f'The time is {self.robot.get_time()}!')
            self.sense()
            #  print(f"Left sensor: {self.center_left_line_sensor}, Right sensor: {self.center_right_line_sensor}")
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
