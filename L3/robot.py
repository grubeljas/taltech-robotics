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

        self.front_middle_laser = 0
        self.front_right_laser = 0
        self.right_ir = 0
        self.right_ir_initial = 0

        self.crossroad_turn = "left"
        self.starting_orientation = None
        self.current_orientation = None

        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

        self.state = "Finding the line"
        self.no_line_counter = 0

        self.obstacle_phase = "Turning back"
        self.go_back_times = 0
        self.got_off_the_line = False

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

    def go_back(self):
        """Robot goes back."""
        self.right_wheel_speed = -8
        self.left_wheel_speed = -8

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
        if line_direction == "back":
            self.go_back()

        if line_direction == "absent":
            self.no_line_counter += 1
        else:
            self.no_line_counter = 0

        if self.no_line_counter > 500:
            self.state = "Finding the line"

        if self.front_middle_laser < 0.06:
            self.state = "Avoiding obstacle"
            print(self.state)
            self.starting_orientation = self.current_orientation

    def avoid_obstacle(self):
        """Avoid obstacle."""
        if self.obstacle_phase == "Turning back":
            if self.go_back_times > 10:
                self.obstacle_phase = "Turning away"
            self.go_back()
            self.go_back_times += 1
        if self.obstacle_phase == "Turning away":
            if abs(self.starting_orientation - self.current_orientation) > 65:
                self.obstacle_phase = "Moving around"
                self.right_ir_initial = self.right_ir
            else:
                self.turn_left()

        if self.obstacle_phase == "Moving around":
            self.move_around()

        if self.obstacle_phase == "Back on track":
            self.turn_left()
            if self.get_line_direction() == "hard right":
                self.state = "Following the line"
                self.obstacle_phase = "Turning away"

    def move_around(self):
        """Move around."""
        print(self.right_ir)
        if self.right_ir_initial - 20 < self.right_ir < self.right_ir_initial + 20:
            self.go_straight()
        elif self.right_ir < self.right_ir_initial - 100:
            self.go_straight()
        elif self.right_ir < self.right_ir_initial - 20:
            self.gradual_turn_right()
        elif self.right_ir > self.right_ir_initial + 20:
            self.gradual_turn_left()
        if self.get_line_direction() != "absent":
            self.obstacle_phase = "Back on track"
            self.starting_orientation = self.current_orientation

    def sense(self):
        """Sense - gets all the information."""
        self.leftmost_line_sensor = self.robot.get_leftmost_line_sensor()
        self.second_left_line_sensor = self.robot.get_second_line_sensor_from_left()
        self.center_left_line_sensor = self.robot.get_third_line_sensor_from_left()

        self.rightmost_line_sensor = self.robot.get_rightmost_line_sensor()
        self.second_right_line_sensor = self.robot.get_second_line_sensor_from_right()
        self.center_right_line_sensor = self.robot.get_third_line_sensor_from_right()

        self.current_orientation = self.robot.get_rotation()

        self.front_middle_laser = self.robot.get_front_middle_laser()
        self.front_right_laser = self.robot.get_front_right_laser()

    def plan(self):
        """Plan - decides what to do based on the information."""
        if self.state == "Finding the line":
            self.find_the_line()
        elif self.state == "Following the line":
            self.follow_the_line()
        elif self.state == "Avoiding obstacle":
            self.avoid_obstacle()

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
            print(f"Right:{self.front_right_laser}")
            print(f"Middle:{self.front_middle_laser}")
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
