"""L3."""
import PiBot
import math


class Robot:
    """Robot."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.state = "Initialization"
        self.initialization_counter = 0

        # Wheels and speed
        self.SPEED = 0.022  # m/s
        self.wheel_size = self.robot.WHEEL_DIAMETER * math.pi
        self.right_encoder = 0
        self.previous_right_encoder = 0
        self.left_encoder = 0
        self.previous_left_encoder = 0
        self.left_wheel_power = 0
        self.right_wheel_power = 0
        self.left_wheel_adjustment = 8
        self.right_wheel_adjustment = 8
        self.left_wheel_used = False
        self.right_wheel_used = False

        # Line sensors
        self.leftmost_line_sensor = 0
        self.second_left_line_sensor = 0
        self.center_left_line_sensor = 0
        self.rightmost_line_sensor = 0
        self.second_right_line_sensor = 0
        self.center_right_line_sensor = 0
        self.all = []

        # Line
        self.no_line_counter = 0
        self.can_find_line_now = False

        # Obstacle detection
        self.middle_laser_last_results = []
        self.rear_right_ir_last_results = []
        self.middle_laser_actual = None
        self.rear_right_ir_actual = None
        self.initial_right_ir = None
        self.detection_distance = 0.06
        self.filter_size = 7

        self.obstacle_avoidance_step = "Turn away"
        self.starting_orientation = None
        self.current_orientation = None

        self.time = 0
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

    def go_forward(self):
        """Robot goes straight forward."""
        self.left_wheel_power = 1 * self.left_wheel_adjustment
        self.right_wheel_power = 1 * self.right_wheel_adjustment
        self.left_wheel_used = True
        self.right_wheel_used = True

    def go_backward(self):
        """Robot goes straight backward."""
        self.left_wheel_power = -1 * self.left_wheel_adjustment
        self.right_wheel_power = -1 * self.right_wheel_adjustment
        self.left_wheel_used = True
        self.right_wheel_used = True

    def turn_left(self):
        """Robot turns left."""
        self.left_wheel_power = -1 * self.left_wheel_adjustment
        self.right_wheel_power = 1 * self.right_wheel_adjustment
        self.left_wheel_used = True
        self.right_wheel_used = True

    def turn_right(self):
        """Robot turns right."""
        self.left_wheel_power = 1 * self.left_wheel_adjustment
        self.right_wheel_power = -1 * self.right_wheel_adjustment
        self.left_wheel_used = True
        self.right_wheel_used = True

    def gradual_turn_left(self):
        """Robot gradually turns left."""
        self.left_wheel_power = 0
        self.right_wheel_power = 1 * self.right_wheel_adjustment
        self.left_wheel_used = False
        self.right_wheel_used = True

    def gradual_turn_right(self):
        """Robot gradually turns right."""
        self.left_wheel_power = 1 * self.left_wheel_adjustment
        self.right_wheel_power = 0
        self.left_wheel_used = True
        self.right_wheel_used = False

    def gradual_turn_left_backwards(self):
        """Robot gradually turns left."""
        self.left_wheel_power = 0
        self.right_wheel_power = -1 * self.right_wheel_adjustment
        self.left_wheel_used = False
        self.right_wheel_used = True

    def gradual_turn_right_backwards(self):
        """Robot gradually turns right."""
        self.left_wheel_power = -1 * self.left_wheel_adjustment
        self.right_wheel_power = 0
        self.left_wheel_used = True
        self.right_wheel_used = False

    def full_stop(self):
        """Robot doesn't move."""
        self.left_wheel_power = 0
        self.right_wheel_power = 0
        self.left_wheel_used = False
        self.right_wheel_used = False

    def find_the_line(self):
        """Instruction for robot to find the line."""
        if self.center_left_line_sensor < 400 and self.center_right_line_sensor < 400:
            print("Line found!")
            self.state = "Following the line"
        elif self.rightmost_line_sensor < 400 or self.second_right_line_sensor < 400:
            self.turn_right()
        else:
            self.turn_left()

    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        velocity = 0
        if self.robot.get_time() != 0:
            velocity = (self.left_encoder - self.previous_left_encoder) / 360 * self.wheel_size / \
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
            velocity = (self.right_encoder - self.previous_right_encoder) / 360 * self.wheel_size / \
                       (self.time - self.previous_time)
        return velocity

    def power_correction(self):
        """Correct power."""
        right_velocity = abs(self.get_right_velocity())
        left_velocity = abs(self.get_left_velocity())

        if self.right_wheel_used:
            if right_velocity < self.SPEED:
                self.right_wheel_adjustment += 0.05
            elif right_velocity > self.SPEED:
                self.right_wheel_adjustment -= 0.05
        if self.left_wheel_used:
            if left_velocity < self.SPEED:
                self.left_wheel_adjustment += 0.05
            elif left_velocity > self.SPEED:
                self.left_wheel_adjustment -= 0.05

    def median_filter(self, values):
        """Filter whatever values it got."""
        if not values:
            return None

        result_index = len(values) // 2 - 1
        if len(values) % 2 == 1:
            result_index += 1

        return sorted(values)[result_index]

    def process_and_filter_readings(self):
        """Filter all required sensors and get actual results."""
        self.rear_right_ir_last_results = self.rear_right_ir_last_results[-self.filter_size:]
        self.middle_laser_last_results = self.middle_laser_last_results[-self.filter_size:]
        self.rear_right_ir_actual = self.median_filter(self.rear_right_ir_last_results)
        self.middle_laser_actual = self.median_filter(self.middle_laser_last_results)

    def initialize(self):
        """Initial speed correction."""
        if self.initialization_counter < 10 or 20 <= self.initialization_counter < 30:
            self.go_forward()
        elif self.initialization_counter < 20 or 30 <= self.initialization_counter < 35:
            self.go_backward()
        else:
            self.state = "Finding the line"
        self.initialization_counter += 1

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

    def find_obstacle(self):
        """Find an obstacle."""
        if self.middle_laser_actual < self.detection_distance:
            print("Object found!")
            self.full_stop()
            self.state = "Avoiding obstacle"
            self.starting_orientation = self.current_orientation
            self.can_find_line_now = False

    def follow_the_line(self):
        """Instruction for robot to follow the line."""
        line_direction = self.get_line_direction()

        if line_direction == "straight":
            self.go_forward()
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

        if self.no_line_counter > 80:
            self.state = "Finding the line"

        self.find_obstacle()

    def avoid_obstacle(self):
        """Avoid whatever obstacle encountered."""
        if self.obstacle_avoidance_step == "Turn away":
            self.turn_away_from_obstacle()
        if self.obstacle_avoidance_step == "Moving around":
            self.move_around_obstacle()
        if self.obstacle_avoidance_step == "Turning back":
            self.turn_back_to_line()

    def turn_away_from_obstacle(self):
        """Turn away from obstacle."""
        self.turn_left()
        if abs(self.current_orientation - self.starting_orientation) > 88:
            self.initial_right_ir = self.rear_right_ir_actual
            self.obstacle_avoidance_step = "Moving around"
            print(self.obstacle_avoidance_step)

    def move_around_obstacle(self):
        """Move around the obstacle."""
        if self.initial_right_ir * 0.99 < self.rear_right_ir_actual < self.initial_right_ir * 1.01:
            self.go_backward()
        elif self.initial_right_ir * 0.99 >= self.rear_right_ir_actual:
            self.gradual_turn_right_backwards()
        elif self.initial_right_ir * 1.01 <= self.rear_right_ir_actual:
            self.gradual_turn_left_backwards()
        if not self.can_find_line_now and abs(self.starting_orientation - self.current_orientation) > 160:
            self.can_find_line_now = True
            print("Can find line now!")
        if self.get_line_direction() != "absent" and self.can_find_line_now:
            self.obstacle_avoidance_step = "Turning back"
            print(self.obstacle_avoidance_step)
            self.starting_orientation = self.current_orientation

    def turn_back_to_line(self):
        """Turn back to line."""
        self.turn_left()
        if abs(self.current_orientation - self.starting_orientation) > 25:
            self.obstacle_avoidance_step = "Turn away"
            self.state = "Finding the line"

    def sense(self):
        """Sense - gets all the information."""
        self.right_encoder = self.robot.get_right_wheel_encoder()
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.time = self.robot.get_time()

        self.leftmost_line_sensor = self.robot.get_leftmost_line_sensor()
        self.second_left_line_sensor = self.robot.get_second_line_sensor_from_left()
        self.center_left_line_sensor = self.robot.get_third_line_sensor_from_left()

        self.rightmost_line_sensor = self.robot.get_rightmost_line_sensor()
        self.second_right_line_sensor = self.robot.get_second_line_sensor_from_right()
        self.center_right_line_sensor = self.robot.get_third_line_sensor_from_right()

        self.current_orientation = self.robot.get_rotation()

        self.middle_laser_last_results.append(self.robot.get_front_middle_laser())
        self.rear_right_ir_last_results.append(self.robot.get_rear_right_side_ir())

        self.process_and_filter_readings()

    def plan(self):
        """Plan - decides what to do based on the information."""
        self.power_correction()

        if self.state == "Initialization":
            self.initialize()
        if self.state == "Finding the line":
            self.find_the_line()
        if self.state == "Following the line":
            self.follow_the_line()
        if self.state == "Avoiding obstacle":
            self.avoid_obstacle()

        self.previous_right_encoder = self.right_encoder
        self.previous_left_encoder = self.left_encoder
        self.previous_time = self.time

        if self.shutdown:
            self.left_wheel_power = 0
            self.right_wheel_power = 0

    def act(self):
        """Act - does stuff based on the decision made."""
        self.robot.set_left_wheel_speed(self.left_wheel_power)
        self.robot.set_right_wheel_speed(self.right_wheel_power)

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
