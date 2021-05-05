"""S1."""
import PiBot
import statistics
import math

#TODO make buffers for objects so that distance is more reliable. Fix end condition (final overrides everything else)


class Robot:
    """Robot class."""

    def __init__(self, state="seek"):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.state = state
        self.shutdown = False
        self.front_laser = 0
        self.front_laser_cache = []

        self.rotation = 0
        self.front_laser_degree_cache = []
        self.object_locations_cache = []
        self.object_locations = []
        self.object_degrees = []

        self.WHEEL_DIAMETER = 0.03
        self.AXIS_LENGTH = 0.132
        self.noise_filter = 0

        # wheels
        self.base_speed = 8
        self.left_speed = -8
        self.right_speed = 8
        self.driving_speed = [-8, 8, 12]

        # start driving coordinates
        self.start_left = 0
        self.start_right = 0

        # # PID
        self.P = 0
        self.Integral = 0
        self.D = 0
        self.left_PID = 0
        self.right_PID = 0
        self.error_left = 0
        self.error_dt_left = 0
        self.error_sum_left = 0
        self.error_diff_left = 0
        self.previous_error_left = 0

        self.error_right = 0
        self.error_dt_right = 0
        self.error_sum_right = 0
        self.error_diff_right = 0
        self.previous_error_right = 0

        # speeds
        self.left_desired_speed = 0
        self.right_desired_speed = 0
        self.actual_left_speed = 0
        self.actual_right_speed = 0

        self.left_encoder = 0
        self.left_last_encoder = 0
        self.left_cycle_encoder = 0
        self.right_encoder = 0
        self.right_last_encoder = 0
        self.right_cycle_encoder = 0

        # time
        self.cycle_time = 0
        self.time = 0
        self.last_time = 0

        # wheel directions
        self.left_direction = -1
        self.right_direction = 1

        # assisting parameters when moving to object
        self.left_desired_speed_add = 0
        self.right_desired_speed_add = 0
        self.stop_noise_filter = 0
        self.rotation = 0

        # ODOMETRY

        # angular velocity
        self.angularLeftVelocity = 0
        self.angularRightVelocity = 0
        self.IMU_odometry = (0, 0, 0)

        # Object locations
        self.object_x = 0
        self.object_y = 0
        self.object2_x = 0
        self.object2_y = 0

        self.object_halfway_x = 0
        self.object_halfway_y = 0

        self.len_of_side = 0
        self.change_x = 0
        self.change_y = 0

        self.stand_at_x = 1000
        self.stand_at_y = 1000
        self.move_to_degree = 0

        self.test = 0
        self.moveint = 0
        self.final = 0
        self.wincondition = 0
        self.move_closer = 0
        self.move_further = 0

        # CAMERA
        self.field_of_view = self.robot.CAMERA_FIELD_OF_VIEW
        self.camera_resolution = self.robot.CAMERA_RESOLUTION
        self.objects = ()
        self.camera_objects = []
        self.objects_cache = []
        self.seek_noise_filter = 0
        self.temp_object = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set Robot reference."""
        self.robot = robot

    def get_object_location(self):
        """Calculate object coordinates, where to move coordinates and then rotation angle for movement."""
        if self.final == 1:
            pass
        elif self.objects[0][2] < self.objects[1][2]:
            self.move_to_degree = self.objects[0][3]
            self.move_further = self.objects[0][2]
            self.move_closer = self.objects[1][2]
            print("red", self.objects[0][3])
        elif self.objects[1][2] <= self.objects[0][2]:
            self.move_to_degree = self.objects[1][3]
            self.move_further = self.objects[1][2]
            self.move_closer = self.objects[0][2]
            print("blue", self.objects[1][3])
        if len(self.objects) > 1 and self.camera_objects:
            print("-BEFORE FINAL,", self.objects[0][3], self.objects[1][3], self.objects[0][3] - self.objects[1][3], self.camera_objects[0])
        if self.camera_objects and self.objects[1]:
            if (130 < abs(self.objects[0][3] - self.objects[1][3]) < 230) and self.camera_objects[0][0] == "blue sphere" and abs(self.objects[0][2] - self.camera_objects[0][2]) < 15:
                self.final = 1
                self.move_to_degree = self.objects[0][3]+90
                self.wincondition = self.objects[0][2]
                self.left_direction = -1
        print("moving")

    def get_x_speed(self, yaw):
        """X coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) * math.cos(math.radians(yaw))

    def get_y_speed(self, yaw):
        """Y coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) * math.sin(math.radians(yaw))

    def get_imu_odometry(self):
        """
        Return the IMU odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder and IMU data. The units must be
           (meters, meters, radians).
        """
        self.IMU_odometry = (self.IMU_odometry[0] + (self.get_x_speed(self.rotation) * self.cycle_time), self.IMU_odometry[1] + (self.get_y_speed(self.rotation) * self.cycle_time), self.rotation)
        return self.IMU_odometry

    def travel_to_object(self):
        """Adjust speed when moving towards object, aiming for its center."""
        if self.rotation > self.move_to_degree:
            self.left_desired_speed_add = 60
            self.right_desired_speed_add = 0
        elif self.rotation < self.move_to_degree:
            self.left_desired_speed_add = 0
            self.right_desired_speed_add = 60

    def reset_pid(self):
        """Reset PID when direction is changed."""
        self.error_left = 0
        self.error_dt_left = 0
        self.error_sum_left = 0
        self.error_diff_left = 0
        self.previous_error_left = 0

        self.error_right = 0
        self.error_dt_right = 0
        self.error_sum_right = 0
        self.error_diff_right = 0
        self.previous_error_right = 0

    def if_found_object(self):
        """If object is found, rotate back to its center and start moving forward."""
        if len(self.objects) > 1:
            print(self.rotation, "FOUND_ROTATION", self.move_to_degree, "MOVETODEG", self.stand_at_x, self.stand_at_y, "X,Y")
            if abs(self.rotation - self.move_to_degree) < 5:
                if self.left_direction == -1:
                    self.reset_pid()
                print("gethere?")
                self.left_direction = 1
                self.right_direction = 1
                if self.get_state != "move":
                    self.set_state("move")

    def set_pid_parameters(self, p: float, i: float, d: float):
        """
        Set the PID parameters.

        Arguments:
          p -- The proportional component.
          i -- The integral component.
          d -- The derivative component.
        """
        # Your code here...
        self.P = p
        self.Integral = i
        self.D = d

    def set_left_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.left_desired_speed = speed

    def set_right_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.right_desired_speed = speed

    def get_left_wheel_pid_output(self):
        """
        Get the controller output value for the left motor.

        Returns:
          The controller output value.
        """
        return self.left_PID

    def get_right_wheel_pid_output(self):
        """
        Get the controller output value for the right motor.

        Returns:
          The controller output value.
        """
        return self.right_PID

    def calculate_left_pid_value(self):
        """Calculate left PID value."""
        self.error_left = (self.left_desired_speed + self.left_desired_speed_add) - self.actual_left_speed
        if self.cycle_time > 0:
            self.error_diff_left = (self.error_left - self.previous_error_left) / self.cycle_time
        else:
            self.error_diff_left = 0
        self.previous_error_left = self.error_left
        self.error_dt_left += self.error_left * self.cycle_time
        result = self.P * self.error_left + self.Integral * self.error_dt_left + self.D * self.error_diff_left
        return result

    def calculate_right_pid_value(self):
        """Calculate right PID value."""
        self.error_right = (self.right_desired_speed + self.right_desired_speed_add) - self.actual_right_speed
        if self.cycle_time > 0:
            self.error_diff_right = (self.error_right - self.previous_error_right) / self.cycle_time
        else:
            self.error_diff_right = 0
        self.previous_error_right = self.error_right
        self.error_dt_right += self.error_right * self.cycle_time
        result = self.P * self.error_right + self.Integral * self.error_dt_right + self.D * self.error_diff_right
        return result

    def get_actual_speed_left(self):
        """Calculate actual speed of left wheel."""
        if not self.cycle_time == 0:
            return self.left_cycle_encoder / self.cycle_time
        else:
            return 0

    def get_actual_speed_right(self):
        """Calculate actual speed of right wheel."""
        if not self.cycle_time == 0:
            return self.right_cycle_encoder / self.cycle_time
        else:
            return 0

    def get_state(self) -> str:
        """
        Get the state.

        Returns:
          The state as a string.
        """
        return self.state

    def set_state(self, state: str):
        """
        Set the current state.

        Arguments:
          state - the state as a string.
        """
        print("CHANGEDSTATE FROM ", self.state, "TO", state)
        self.state = state

    def get_objects(self) -> list:
        """
        Return the list with the detected objects so far.

        (i.e., add new objects to the list as you detect them).

        Returns:
          The list with detected object angles, the angles are in
          degrees [0..360), 0 degrees being the start angle and following
          the right-hand rule (e.g., turning left 90 degrees is 90, turning
          right 90 degrees is 270 degrees).
        """
        return self.object_degrees

    def get_front_middle_laser(self):
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        if self.front_laser < 0.5:
            self.noise_filter += 1
            self.front_laser_degree_cache.insert(0, self.rotation)
            self.object_locations_cache.insert(0, self.front_laser)
        elif self.noise_filter > 0:
            self.noise_filter -= 1
            self.front_laser_degree_cache.pop(0)
            self.object_locations_cache.pop(0)
        if self.front_laser < 0.5 and self.noise_filter > 3:
            self.front_laser_degree_cache.insert(0, self.rotation)
        elif self.front_laser_degree_cache and self.noise_filter > 3:
            self.object_degrees.append(statistics.median(self.front_laser_degree_cache))
            self.object_locations.append(statistics.median(self.object_locations_cache))
            self.front_laser_degree_cache.clear()
            self.object_locations_cache.clear()
            self.noise_filter = 0

    def process_camera_data(self):
        """Calculate x and y based on camera data."""
        self.camera_objects = tuple(self.camera_objects)
        for item in self.camera_objects:
            self.deg = self.get_object_angle(item[1][0])
            current = item + ((self.rotation) % 360,)
            if not self.objects:
                self.objects = (current,)
                break
            elif not current[0] == self.objects[-1][0] and len(self.objects) < 2:
                self.objects = self.objects + (current,)

        objects_copy = ()
        for item in self.objects:
            x = 25/(item[2] * math.cos(math.radians(item[3])))
            y = 25/(item[2] * math.sin(math.radians(item[3])))
            objects_copy += ((item[0], (x, y), item[2], item[3]),)
        self.objects = objects_copy
        if self.objects:
            if len(self.objects_cache) >= 5:
                self.objects_cache.pop(0)
            self.objects_cache.append(self.objects)
            if len(self.objects_cache[-1]) != len(self.objects):
                self.objects_cache = []
            median_array = []
            if len(self.objects_cache) >= 5:
                for k in range(len(self.objects_cache)):
                    median_array.append(self.objects_cache[k][0][2])
                median = statistics.median(median_array)
                for i in range(len(self.objects_cache)):
                    if self.objects_cache[i][0][2] == median:
                        self.objects = self.objects_cache[i]
                return self.objects
        return None

    def get_object_angle(self, x):
        """calculate  object angle relative to robot."""
        deg = ((self.camera_resolution[0] / 2 - x) / self.camera_resolution[0]) * self.field_of_view[0]
        return deg

    def sense(self):
        """Sense method according to the SPA architecture."""
        self.front_laser = self.robot.get_front_middle_laser()
        self.camera_objects = self.robot.get_camera_objects()
        self.rotation = self.robot.get_rotation() % 360

        self.time = self.robot.get_time()
        self.cycle_time = self.time - self.last_time
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()
        self.left_cycle_encoder = self.left_encoder - self.left_last_encoder
        self.right_cycle_encoder = self.right_encoder - self.right_last_encoder
        self.actual_left_speed = self.get_actual_speed_left()
        self.actual_right_speed = self.get_actual_speed_right()

        self.left_PID = self.calculate_left_pid_value()
        self.right_PID = self.calculate_right_pid_value()

        self.last_time = self.time
        self.left_last_encoder = self.left_encoder
        self.right_last_encoder = self.right_encoder

        if self.cycle_time > 0:
            self.angularLeftVelocity = ((math.radians(self.left_cycle_encoder) / self.cycle_time))
            self.angularRightVelocity = ((math.radians(self.right_cycle_encoder) / self.cycle_time))
        else:
            self.angularLeftVelocity = 0
            self.angularRightVelocity = 0

        self.get_imu_odometry()
        if self.get_state() == "move" and self.final == 0:
            if self.camera_objects:
                print("movingtest", self.moveint, self.camera_objects[0][2], "in front", self.move_closer, "closer")
                self.temp_object =  self.camera_objects[0][2]
            if len(self.camera_objects) < 2 and (self.camera_objects is None or self.temp_object > self.move_closer or self.camera_objects[0][2] > 90):
                self.seek_noise_filter += 1
                if self.seek_noise_filter > 2:
                    self.set_state("seek")
                    self.objects = tuple()
                    self.camera_objects = []
                    self.left_direction = -1
                    self.reset_pid()
                    self.move_to_degree = 0
                    self.moveint = 0
                    self.seek_noise_filter = 0
                    self.objects_cache = []
            else:
                self.seek_noise_filter = 0
            print("after_moving_test")
        if self.get_state() == "seek":
            self.process_camera_data()
        if len(self.objects) > 1:
            self.get_object_location()
        print(self.objects, "OBJECTS", self.move_to_degree, "MOVETODEGREE", self.state, "STATE")

    def plan(self):
        """The plan method in the SPA architecture."""
        if self.final == 0:
            self.if_found_object()
        self.set_pid_parameters(0.008, 0.00, 0.000016)
        self.set_left_wheel_speed(60 * self.left_direction)
        self.set_right_wheel_speed(60 * self.right_direction)
        if self.right_direction == 1 and self.left_direction == 1:
            print(self.IMU_odometry, "IMUODO")
            self.travel_to_object()
        if self.camera_objects:
            print(self.final, "FINAL", self.wincondition, self.camera_objects[0][2])
        if self.final == 1 and abs(self.move_to_degree - self.rotation) < 15:
            if self.stop_noise_filter > 2:
                print("STOP------------")
                self.shutdown = True
            self.stop_noise_filter += 1
        else:
            self.stop_noise_filter = 0

    def act(self):
        """The act method in SPA architecture."""
        self.robot.set_left_wheel_speed(9 * self.left_direction + self.get_left_wheel_pid_output())
        self.robot.set_right_wheel_speed(9 * self.right_direction + self.get_right_wheel_pid_output())
        if self.shutdown:
            self.robot.set_left_wheel_speed(0)
            self.robot.set_right_wheel_speed(0)
        self.robot.set_grabber_height(0)

    def spin(self):
        """The main loop."""
        while not self.shutdown:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.03)


def main():
    """The  main entry point."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
