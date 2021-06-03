"""M1 - Maze."""
import math

import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        # ROBOT
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.wheel_radius = self.robot.WHEEL_DIAMETER / 2
        self.forward_vector = list()
        self.side_vector = list()

        # IR SENSORS
        self.l_side_ir = 0
        self.r_side_ir = 0
        self.l_straight_ir = 0
        self.r_straight_ir = 0
        self.l_side_buffer = list()
        self.r_side_buffer = list()
        self.l_straight_buffer = list()
        self.r_straight_buffer = list()

        # LASER
        self.middle_laser_buffer = list()

        # TIME
        self.actual_time = 0
        self.previous_time = 0
        self.time_delta = 0
        self.timer = 0

        # ENCODERS
        self.right_encoder_actual = 0
        self.left_encoder_actual = 0
        self.right_encoder_previous = 0
        self.left_encoder_previous = 0
        self.left_encoder_delta = 0
        self.right_encoder_delta = 0

        # ROBOT POSITION
        self.x_pos = 0
        self.y_pos = 0

        # ROBOT STATE
        self.state = "move_forward"

        # ROTATION
        self.rotation = 180
        self.degrees_counter = 0
        self.distance_counter = 0
        self.stage = 1
        self.rotation_buffer = list()

        # MOVING
        self.toDo = "moving"
        self.direction = -1
        self.right_wheel = 0
        self.left_wheel = 0
        self.custom_moving_option = tuple()
        self.moving_options = {
            "correction": {-1: (-150, -250), 1: (-250, -150)},
            "turning": {-1: (-150, -350), 1: (-350, -150)},
            "spinning": {-1: (100, -100), 1: (-100, 100)}
        }

        # ROTATION
        self.rotation_memory = 0
        self.rotation_delta = 0
        self.actual_rotation = 0
        self.previous_rotation = 0

        # MAP
        self.map = list()
        self.actual_point = [0, 0]
        self.next_point = list()
        self.map_direction = "RIGHT"
        self.directions_dict = {"RIGHT": ("UP", "DOWN"),
                                "LEFT": ("DOWN", "UP"),
                                "UP": ("LEFT", "RIGHT"),
                                "DOWN": ("RIGHT", "LEFT")}

        self.wall_forward = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot."""
        self.robot = robot

    def sense(self):
        """Sense."""
        # UPDATE LASERS
        self.middle_laser_buffer.append(self.robot.get_front_middle_laser())
        self.middle_laser_buffer = self.middle_laser_buffer[-5:]

        # UPDATE IR
        self.l_side_ir = self.robot.get_rear_left_side_ir()
        self.r_side_ir = self.robot.get_rear_right_side_ir()

        # UPDATE ENCODERS
        self.left_encoder_previous = self.left_encoder_actual
        self.left_encoder_actual = self.robot.get_left_wheel_encoder()
        self.right_encoder_previous = self.right_encoder_actual
        self.right_encoder_actual = self.robot.get_right_wheel_encoder()
        self.left_encoder_delta = self.left_encoder_actual - self.left_encoder_previous
        self.right_encoder_delta = self.right_encoder_actual - self.right_encoder_previous

        # UPDATE TIME
        self.previous_time = self.actual_time
        self.actual_time = self.robot.get_time()
        self.time_delta = self.actual_time - self.previous_time

        # UPDATE ROTATION
        self.previous_rotation = self.actual_rotation
        self.actual_rotation = self.robot.get_rotation()

        self.rotation_delta = self.actual_rotation - self.previous_rotation
        self.rotation += self.rotation_delta
        self.rotation %= 360

        # UPDATE ODOMETRY
        self.update_odometry()

        # UPDATE VECTOR
        self.forward_vector = self.get_object_coords([self.x_pos, self.y_pos], -1, self.rotation)
        self.side_vector = self.get_object_coords([self.x_pos, self.y_pos], 1, self.rotation - 90)

    def plan(self):
        """Plan."""
        if self.state == "move_forward":
            self.move_forward()

        if self.toDo == "moving":
            self.speed_calibrating(-200, -200)
        elif self.toDo == "stop":
            self.speed_calibrating(0, 0)
        else:
            options = self.moving_options[self.toDo][self.direction]
            self.speed_calibrating(options[0], options[1])

    def act(self):
        """Act."""
        self.robot.set_left_wheel_speed(self.left_wheel)
        self.robot.set_right_wheel_speed(self.right_wheel)

    def get_left_velocity(self) -> float:
        """Left wheel angular velocity."""
        return (self.left_encoder_actual - self.left_encoder_previous) / self.time_delta

    def get_right_velocity(self) -> float:
        """Right wheel angular velocity."""
        return (self.right_encoder_actual - self.right_encoder_previous) / self.time_delta

    def speed_calibrating(self, l_speed: int, r_speed: int):
        """Softening of movement based on actual angular velocity."""
        right_speed = self.get_right_velocity()
        left_speed = self.get_left_velocity()

        right_index = abs(right_speed - r_speed) / 400 if abs(right_speed - r_speed) < 120 else 0.5
        left_index = abs(left_speed - l_speed) / 400 if abs(left_speed - l_speed) < 120 else 0.5

        self.right_wheel = 8 if r_speed > 0 and self.right_wheel < 8 else self.right_wheel
        self.right_wheel = -8 if r_speed < 0 and self.right_wheel > -8 else self.right_wheel
        self.left_wheel = 8 if l_speed > 0 and self.left_wheel < 8 else self.left_wheel
        self.left_wheel = -8 if l_speed < 0 and self.left_wheel > -8 else self.left_wheel

        self.right_wheel = self.right_wheel + right_index if right_speed < r_speed else self.right_wheel - right_index
        self.left_wheel = self.left_wheel + left_index if left_speed < l_speed else self.left_wheel - left_index

        self.right_wheel = 0 if r_speed == 0 else self.right_wheel
        self.left_wheel = 0 if l_speed == 0 else self.left_wheel

    # ODOMETRY
    def get_object_coords(self, relative_obj, distance, rotation):
        """Object coords by distance and angle."""
        x = relative_obj[0]
        y = relative_obj[1]
        x += distance * math.cos(math.radians(rotation))
        y += distance * math.sin(math.radians(rotation))
        return [x, y]

    # UPDATE ODOMETRY
    def update_odometry(self):
        """Docstring."""
        distance = (math.radians(self.left_encoder_delta) + math.radians(self.right_encoder_delta)) / 2 * self.wheel_radius
        new_coords = self.get_object_coords([self.x_pos, self.y_pos], distance, self.rotation)
        self.x_pos = new_coords[0]
        self.y_pos = new_coords[1]

    def go_to_coords(self, coord: list, spinning_turn: bool):
        """Go to the target position [x, y]."""
        direction = self.get_direction_to_coords(coord)
        print(f"direction: {direction}")
        if abs(direction) < 5:
            self.toDo = "moving"
        elif abs(direction) < 10:
            self.toDo = "correction"
        else:
            if spinning_turn:
                self.toDo = "spinning"
            else:
                self.toDo = "turning"

        if direction < 0:
            self.direction = -1
        else:
            self.direction = 1

    def get_middle_laser(self) -> float:
        """Middle laser."""
        if self.middle_laser_buffer:
            return sorted(self.middle_laser_buffer)[len(self.middle_laser_buffer) // 2]
        return 0

    def check_map_direction(self):
        """Check map dir."""
        if self.l_side_ir < 500:
            self.wall_forward = False
            self.map_direction = self.directions_dict[self.map_direction][1]
        elif self.r_side_ir < 500:
            self.wall_forward = False
            self.map_direction = self.directions_dict[self.map_direction][0]

    def get_next_square_midpoint(self):
        """Get next square."""
        object_x = self.actual_point[0]
        object_y = self.actual_point[1]
        if self.map_direction == "RIGHT":
            return [object_x + 0.31, object_y]
        elif self.map_direction == "LEFT":
            return [object_x - 0.31, object_y]
        elif self.map_direction == "UP":
            return [object_x, object_y + 0.32]
        elif self.map_direction == "DOWN":
            return [object_x, object_y - 0.32]

    def get_cartesian_distance(self, target: list) -> float:
        """Return distance between robot and target [x, y]."""
        return math.sqrt((self.x_pos - target[0]) ** 2 + (self.y_pos - target[1]) ** 2)

    def get_direction_to_coords(self, target: list):
        """Return the angle to the target [x, y]."""
        target_x = target[0]
        target_y = target[1]

        vector_object_dist = math.sqrt((self.forward_vector[0] - target_x) ** 2 + (self.forward_vector[1] - target_y) ** 2)
        side_vector_object_dist = math.sqrt((self.side_vector[0] - target_x) ** 2 + (self.side_vector[1] - target_y) ** 2)
        target_robot_dist = self.get_cartesian_distance(target)
        if -1 <= (1 + target_robot_dist ** 2 - vector_object_dist ** 2) / (2 * target_robot_dist) <= 1:
            s = math.acos((1 + target_robot_dist ** 2 - vector_object_dist ** 2) / (2 * target_robot_dist))
            if -1 <= (1 + target_robot_dist ** 2 - side_vector_object_dist ** 2) / (2 * target_robot_dist) <= 1:
                a = math.acos((1 + target_robot_dist ** 2 - side_vector_object_dist ** 2) / (2 * target_robot_dist * 0.1))
                a = math.degrees(a)
                s = math.degrees(s)
                if a > 90:
                    s = -s
                return s
        return 0

    def move_forward(self):
        """Move forward to the next point."""
        self.next_point = self.get_next_square_midpoint()
        print(self.next_point)
        self.go_to_coords(self.next_point, True)
        if self.get_cartesian_distance(self.next_point) <= 0.05:
            self.actual_point = self.next_point
            if self.r_straight_ir < 500:
                self.check_map_direction()

    def spin(self):
        """The main spin loop."""
        while True:
            print("__________________________________________________________________")
            self.sense()
            self.plan()
            print(f"right_side_ir: {self.r_side_ir}")
            print(f"left_side_ir: {self.l_side_ir}")
            print(f"l_wheel: {self.left_wheel} || r_wheel: {self.right_wheel}")
            print(f"x: {round(self.x_pos, 2)} || y: {round(self.y_pos, 2)}")
            print(f"state: {self.state}")
            print(f"doing: {self.toDo}")
            print(f"current_dir {self.map_direction}")
            print(f"bool: {self.wall_forward}")
            print(f"DIR: {self.direction}")
            print(f"rotation: {self.rotation}")
            self.act()
            self.robot.sleep(0.05)


def main():
    """Main entry point."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
