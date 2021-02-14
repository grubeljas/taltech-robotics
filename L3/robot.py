"""L3."""
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

        self.prev_rear_left_straight = 0
        self.prev_rear_left_diagonal = 0
        self.prev_rear_left_side = 0

        self.prev_rear_right_straight = 0
        self.prev_rear_right_diagonal = 0
        self.prev_rear_right_side = 0

        self.rear_left_straight_ir = self.robot.get_rear_left_straight_ir()
        self.rear_left_diagonal_ir = self.robot.get_rear_left_diagonal_ir()
        self.rear_left_side_ir = self.robot.get_rear_left_side_ir()

        self.rear_right_straight_ir = self.robot.get_rear_right_straight_ir()
        self.rear_right_diagonal_ir = self.robot.get_rear_right_diagonal_ir()
        self.rear_right_side_ir = self.robot.get_rear_right_side_ir()


        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        self.state = "Finding the line"
        self.no_line_counter = 0
        self.bypass_counter = 0


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


    def get_line_direction(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
           right: Line is on the right (i.e., the robot should turn right to reach the line again)
           straight: Robot is on the line (i.e., the robot should not turn to stay on the line)
           left: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        if self.center_left_line_sensor < 400 and self.center_right_line_sensor < 400:
            line_direction = "straight"
        elif self.leftmost_line_sensor < 400 or self.second_left_line_sensor < 400:
            line_direction = "left"
        elif self.rightmost_line_sensor < 400 or self.second_right_line_sensor < 400:
            line_direction = "right"
        elif self.center_left_line_sensor < 400:
            line_direction = "leaning left"
        elif self.center_right_line_sensor < 400:
            line_direction = "leaning right"
        else:
            line_direction = "absent"
        return line_direction

    def follow_the_line(self):
        """Instruction for robot to follow the line."""
        line_direction = self.get_line_direction()
        if line_direction == "straight":
            self.go_straight()
        elif line_direction == "right":
            self.gradual_turn_right()
        elif line_direction == "left":
            self.gradual_turn_left()
        elif line_direction == "leaning left":
            self.gradual_turn_left()
        elif line_direction == "leaning right":
            self.gradual_turn_right()
        elif line_direction == "absent":
            self.no_line_counter += 1
            print(f"No line counter = {self.no_line_counter}")
        if self.rear_right_straight_ir < 400:
            self.turn_left()
            self.state = "Bypassing"

        if self.no_line_counter > 0 and line_direction != "absent":
            self.no_line_counter = 0
        elif self.no_line_counter > 50:
            self.state = "Finding the line"

    def do_bypass(self):
        """Ride around tha object on the left."""
        print("Bypass")
        self.bypass_counter += 1
        if self.rear_left_diagonal_ir < 0.07:
            self.go_straight()
        else:
            self.turn_left()
            self.state = "Finding the line"

    def sense(self):
        """Sense - gets all the information."""
        if self.robot.get_time() % 0.1 < 0.05:
            print(f'The time is {self.robot.get_time()}!')
            self.prev_rear_left_straight = self.rear_left_straight_ir
            self.prev_rear_left_diagonal = self.rear_left_diagonal_ir
            self.prev_rear_left_side = self.rear_left_side_ir
            self.prev_rear_right_straight = self.rear_right_straight_ir
            self.prev_rear_right_diagonal = self.rear_right_diagonal_ir
            self.prev_rear_right_side = self.rear_right_side_ir
            print(f"INFRARED{self.robot.get_rear_irs()}")

        self.rear_left_straight_ir = self.robot.get_rear_left_straight_ir()
        self.rear_left_diagonal_ir = self.robot.get_rear_left_diagonal_ir()
        self.rear_left_side_ir = self.robot.get_rear_left_side_ir()

        self.rear_right_straight_ir = self.robot.get_rear_right_straight_ir()
        self.rear_right_diagonal_ir = self.robot.get_rear_right_diagonal_ir()
        self.rear_right_side_ir = self.robot.get_rear_right_side_ir()

        self.leftmost_line_sensor = self.robot.get_leftmost_line_sensor()
        self.second_left_line_sensor = self.robot.get_second_line_sensor_from_left()
        self.center_left_line_sensor = self.robot.get_third_line_sensor_from_left()

        self.rightmost_line_sensor = self.robot.get_rightmost_line_sensor()
        self.second_right_line_sensor = self.robot.get_second_line_sensor_from_right()
        self.center_right_line_sensor = self.robot.get_third_line_sensor_from_right()

    def plan(self):
        """Plan - decides what to do based on the information."""
        if self.state == "Finding the line":
            self.find_the_line()
        elif self.state == "Following the line":
            self.follow_the_line()
        elif self.state == "Bypassing":
            self.do_bypass()

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

            self.sense()
            #print(f"Left sensor: {self.center_left_line_sensor}, Right sensor: {self.center_right_line_sensor}")
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
