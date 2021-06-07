"""O2 - Bronze objects."""
import PiBot
import math


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()

        self.robot_current_state = "scan"

        self.distance_from_first_object = 0
        self.first_object_location_angle = 0

        self.distance_from_second_object = 0
        self.second_object_location_angle = 0

        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

        self.front_middle_laser = 0
        self.previous_front_middle_laser = 0

        self.left_wheel_encoder = 0

        self.current_rotation = 0

        self.first_object_found = False
        self.second_object_found = False

        self.triangle_side_length = 0

        self.adjusting_position = False
        self.position_adjusting_phase = ""
        self.last_adjusted_by = ""

        self.phase_counter = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.

        """
        self.robot = robot

    def sense(self):
        """Sensing block."""
        self.left_wheel_encoder = self.robot.get_left_wheel_encoder()
        self.current_rotation = self.robot.get_rotation()
        self.previous_front_middle_laser = self.front_middle_laser
        self.front_middle_laser = self.robot.get_front_middle_laser()

    def act(self):
        """Acting block."""
        self.robot.set_left_wheel_speed(self.left_wheel_speed)
        self.robot.set_right_wheel_speed(self.right_wheel_speed)

    def plan(self):
        """Planning block."""
        print(f"Laser value: {self.front_middle_laser}")

        if self.first_object_found is False or self.second_object_found is False:
            self.robot_current_state = "scan"
            self.objects_localization()

        elif self.adjusting_position is True:
            if self.phase_counter < 5:
                print(f"Adjusting phase: {self.position_adjusting_phase}")
                print(self.robot_current_state)
                print(f"Wheel speeds: {self.left_wheel_speed, self.right_wheel_speed}")
                if self.position_adjusting_phase == "change":
                    self.change_from_one_obstacle_to_another()
                elif self.position_adjusting_phase == "second":
                    self.change_position_compared_to_second_object()
                elif self.position_adjusting_phase == "first":
                    self.change_position_compared_to_first_object()
            else:
                self.robot_current_state = "stop"
                print("OBJECT FOUND.")
                print(
                    f"DISTANCE FROM FIRST: {self.distance_from_first_object}, DISTANCE FROM SECOND: {self.distance_from_second_object}, DISTANCE FROM EACHOTHER: {self.triangle_side_length}")

        self.set_wheel_speeds()

    def objects_localization(self):
        """Method for detecting objects and calculating distances."""
        if self.previous_front_middle_laser - self.front_middle_laser > 0.3 and abs(self.left_wheel_encoder) > 3:
            if self.first_object_found is False:
                print("FIRST OBJECT")
                self.first_object_found = True
                self.distance_from_first_object = self.front_middle_laser
                self.first_object_location_angle = self.current_rotation
            elif self.first_object_found is True and self.second_object_found is False:
                print("SECOND OBJECT")
                self.second_object_found = True
                self.distance_from_second_object = self.front_middle_laser
                self.second_object_location_angle = self.current_rotation
                self.robot_current_state = "stop"

                initial_angle_between_objects_in_degrees = self.first_object_location_angle - self.second_object_location_angle
                initial_angle_between_objects_in_radians = math.radians(initial_angle_between_objects_in_degrees)
                self.triangle_side_length = math.sqrt((self.distance_from_first_object ** 2)
                                                      + (self.distance_from_second_object ** 2) - 2
                                                      * self.distance_from_first_object
                                                      * self.distance_from_second_object
                                                      * math.cos(initial_angle_between_objects_in_radians))
                self.adjusting_position = True
                self.position_adjusting_phase = "second"
                print("Starting adjusting position")
                print(f"Angle with objects: {initial_angle_between_objects_in_degrees}")
                print(f"Triangle side length: {self.triangle_side_length}")

    def change_from_one_obstacle_to_another(self):
        """Method to look for other obstacle."""
        if self.previous_front_middle_laser - self.front_middle_laser < 0.3:
            if self.last_adjusted_by == "second":
                self.robot_current_state = "hard turn right"
            elif self.last_adjusted_by == "first":
                self.robot_current_state = "hard turn left"
        else:
            if self.last_adjusted_by == "second":
                self.position_adjusting_phase = "first"
            elif self.last_adjusted_by == "first":
                self.position_adjusting_phase = "second"

    def change_position_compared_to_second_object(self):
        """Method for changing position compared to second object."""
        if abs(self.triangle_side_length - self.front_middle_laser) > 0.01:
            if self.front_middle_laser > self.triangle_side_length:
                self.robot_current_state = "drive forward"
                self.distance_from_second_object = self.front_middle_laser
            elif self.distance_from_second_object < self.triangle_side_length:
                self.robot_current_state = "reverse"
                self.distance_from_second_object = self.front_middle_laser
        else:
            self.phase_counter += 1
            print("OTHER OBSTACLE")
            self.distance_from_second_object = self.front_middle_laser
            self.last_adjusted_by = "second"
            self.position_adjusting_phase = "change"

    def change_position_compared_to_first_object(self):
        """Method for chaning position compared to first object."""
        if abs(self.triangle_side_length - self.front_middle_laser) > 0.01:
            if self.front_middle_laser > self.triangle_side_length:
                self.robot_current_state = "drive forward"
                self.distance_from_first_object = self.front_middle_laser
            elif self.front_middle_laser < self.triangle_side_length:
                self.robot_current_state = "reverse"
                self.distance_from_first_object = self.front_middle_laser
        else:
            self.phase_counter += 1
            self.distance_from_first_object = self.front_middle_laser
            self.last_adjusted_by = "first"
            self.position_adjusting_phase = "change"

    def set_wheel_speeds(self):
        """Method for setting wheel speeds according to state."""
        if self.robot_current_state == "drive forward":
            self.left_wheel_speed = 8
            self.right_wheel_speed = 8
        if self.robot_current_state == "stop":
            self.left_wheel_speed = 0
            self.right_wheel_speed = 0
        if self.robot_current_state == "hard turn left":
            self.left_wheel_speed = -8
            self.right_wheel_speed = 8
        if self.robot_current_state == "scan":
            self.left_wheel_speed = -8
            self.right_wheel_speed = 8

        if self.robot_current_state == "reverse":
            self.left_wheel_speed = -8
            self.right_wheel_speed = -8
        if self.robot_current_state == "hard turn right":
            self.right_wheel_speed = -8
            self.left_wheel_speed = 8

    def spin(self):
        """Looping block."""
        while True:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.05)


def main():
    """
    The main function.

    Create a Robot class object and run it.
    """
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
