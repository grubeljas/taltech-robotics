"""OT11 - World model."""
import PiBot
import math


class Robot:
    """The robot class."""

    def __init__(self, initial_odometry=[0.201, -0.148, 1.529]):
        """
        Initialize variables.

        Arguments:
          initial_odometry -- Initial odometry(start position and angle),
                              [x, y, yaw] in [meters, meters, radians]
        """
        self.robot = PiBot.PiBot()

        # ODOMETRY
        self.truth = 0

        self.encoder_odometry = (initial_odometry[0], initial_odometry[1], initial_odometry[2])

        # encoders
        self.left_encoder = 0
        self.left_last_encoder = 0
        self.left_cycle_encoder = 0
        self.right_encoder = 0
        self.right_last_encoder = 0
        self.right_cycle_encoder = 0

        # time
        self.time = 0
        self.last_time = 0
        self.cycle_time = 0

        # angular velocity
        self.angularLeftVelocity = 0
        self.angularRightVelocity = 0

        # VISION PROCESSING

        self.camera_objects = []
        self.resolution = self.robot.CAMERA_RESOLUTION
        self.field_of_view = self.robot.CAMERA_FIELD_OF_VIEW
        self.closest_object = ["", (0, 0), 0]
        self.current_object = ["", (0, 0), 0]
        self.closest_index = 0
        self.closest_x = 0

        self.max_width = 0
        self.rad = 0

        # general

        self.camera_objects_copy = 0
        self.item_dict = {}
        self.object_x = 0
        self.object_y = 0
        self.object_diff_x = 0
        self.object_diff_y = 0
        self.yaw = initial_odometry[2]
        self.object_dist = 0

        self.shortest_dist = 10000
        self.shortest_point = 0
        self.euclidean_distance = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

    # ODOMETRY
    def get_x_speed(self, yaw):
        """X coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) * math.cos(yaw)

    def get_y_speed(self, yaw):
        """Y coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) * math.sin(yaw)

    def get_yaw(self):
        """Calculate yaw for encoder odometry."""
        return (self.robot.WHEEL_DIAMETER / 2) / self.robot.AXIS_LENGTH * (self.angularRightVelocity - self.angularLeftVelocity)

    def get_encoder_odometry(self):
        """
        Return the encoder odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder data. The units must be (meters, meters, radians).
        """
        # Your code here...
        self.yaw = self.encoder_odometry[2] + (self.get_yaw() * self.cycle_time)
        if abs(self.angularLeftVelocity + self.angularRightVelocity) <= 0.1:
            self.encoder_odometry = (self.encoder_odometry[0], self.encoder_odometry[1], self.yaw)
        else:
            self.encoder_odometry = (self.encoder_odometry[0] + (self.get_x_speed(self.get_yaw()) * self.cycle_time), self.encoder_odometry[1] + (self.get_y_speed(self.get_yaw()) * self.cycle_time), self.yaw)
        return self.encoder_odometry

    # END ODOMETRY

    # VISION PROCESSING

    def get_closest_visible_object_angle(self):
        """
        Find the closest visible object from the objects list.

        Returns:
          The angle (in radians) to the closest object w.r.t. the robot
          orientation (i.e., 0 is directly ahead) following the right
          hand rule (i.e., objects to the left have a plus sign and
          objects to the right have a minus sign).
          Must return None if no objects are visible.
        """
        for item in range(len(self.camera_objects)):
            self.current_object = self.camera_objects[item]
            if self.current_object[2] > self.closest_object[2]:
                self.closest_object = self.current_object
                self.closest_index = item
                self.closest_x = self.closest_object[1][0]
        if self.max_width and len(self.camera_objects) > 0:
            # print(self.field_of_view, "FIELD OF VIEW WxH")
            self.rad = math.radians(((self.max_width / 2 - self.closest_x) / self.max_width) * self.field_of_view[0])
            self.rad = self.rad % math.pi
            print(self.rad, "RADs")
            return self.rad
        return None

    def update_world(self) -> None:
        """Update the world model (insert objects into memory)."""
        for item in range(len(self.camera_objects)):

            if self.max_width and len(self.camera_objects) > 0:
                print(self.field_of_view)
                self.rad = math.radians(
                    ((self.max_width / 2 - self.camera_objects[item][1][0]) / self.max_width) * self.field_of_view[0])
                self.rad = self.rad % math.pi

            self.object_dist = 30 / self.camera_objects[item][2]
            self.object_diff_x = self.object_dist / math.cos(self.rad)
            self.object_diff_y = self.object_dist * math.tan(self.rad)
            self.object_x = (math.cos(self.yaw) * self.object_diff_x + math.sin(self.yaw) * self.object_diff_y)
            self.object_y = (math.sin(-self.yaw) * self.object_diff_x + math.cos(self.yaw) * self.object_diff_y)
            print(self.yaw, "robot YAW", self.rad, "Object yaw from robot")
            self.item_dict[item + len(self.item_dict)] = (self.encoder_odometry[0] + self.object_x, self.encoder_odometry[1] + self.object_y)

    def get_closest_object_angle(self) -> float:
        """
        Return the angle of the closest object.

        This method returns the angle of the object that is
        the shortest Euclidean distance
        (i.e., the closest object angle w.r.t. the robot heading).

        Returns:
          The normalized (range [0..2*pi]) angle (radians) to the
          closest object w.r.t. the robot heading following
          the right-hand rule.
          E.g., 0 if object is straight ahead,
                1.57 if the object is 90 degrees to the left of the robot.
                3.14 if the closest object is 180 degrees from the robot.
                4.71 if the objectis 90 degrees to the right of the robot.
          None if no objects have been detected.
        """
        # Your code here...
        for item in self.item_dict:
            self.shortest_dist = 10000
            print("X:", self.item_dict[item][0], self.encoder_odometry[0], "Y:", self.item_dict[item][1], self.encoder_odometry[1])
            self.euclidean_distance = math.sqrt(math.pow(self.item_dict[item][0] - self.encoder_odometry[0], 2) + math.pow(self.item_dict[item][1] - self.encoder_odometry[1], 2))
            if self.euclidean_distance < self.shortest_dist:
                self.shortest_dist = self.euclidean_distance
                self.shortest_point = (self.item_dict[item][0], self.item_dict[item][1])
        if self.shortest_point:
            self.yaw_from_zero = math.atan2(self.shortest_point[1], self.shortest_point[0])
            print(self.yaw_from_zero, self.yaw, "YAWFROMZERO AND THEN YAW")
            return (self.yaw_from_zero - self.yaw) % (2 * math.pi)
        else:
            return None
        # angle
        # self.move_to_degree = (math.degrees(math.atan2(self.stand_at_y, self.stand_at_x))) % 360

    def sense(self):
        """SPA architecture sense block."""
        # VISION
        self.camera_objects = self.robot.get_camera_objects()
        self.max_width = self.resolution[0]

        # ODOMETRY
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

        self.time = self.robot.get_time()

        # cycle times
        self.cycle_time = self.time - self.last_time
        self.left_cycle_encoder = self.left_encoder - self.left_last_encoder
        self.right_cycle_encoder = self.right_encoder - self.right_last_encoder

        if self.cycle_time > 0:
            self.angularLeftVelocity = ((math.radians(self.left_cycle_encoder) / self.cycle_time))
            self.angularRightVelocity = ((math.radians(self.right_cycle_encoder) / self.cycle_time))
        else:
            self.angularLeftVelocity = 0
            self.angularRightVelocity = 0

        # get true data (for testing purposes)
        self.truth = self.robot.get_ground_truth()

        self.get_encoder_odometry()
        if not (self.camera_objects == self.camera_objects_copy):
            self.update_world()
            self.camera_objects_copy = self.camera_objects.copy()
            print(self.camera_objects_copy, self.camera_objects, "CAMOCJ")
        print(self.item_dict, "ITEMDICT")
        self.get_closest_object_angle()
        print("----------------", self.shortest_point, "CLOSEST OBJECT", self.get_closest_object_angle(), "ANGLE", self.yaw, "YAW")
        print(self.angularLeftVelocity, self.angularRightVelocity, "velocities")
        print("ENCODER ODO", self.encoder_odometry)
        print("TRUTH", self.truth)

        self.last_time = self.time
        self.left_last_encoder = self.left_encoder
        self.right_last_encoder = self.right_encoder

    def spin(self):
        """Spin loop."""
        for _ in range(100):
            self.sense()
            print(f"objects = {self.robot.get_camera_objects()}")
            self.robot.sleep(0.05)


def main():
    """The main entry point."""
    robot = Robot()
    import turn_and_straight  # or any other data file
    data = turn_and_straight.get_data()
    robot.robot.load_data_profile(data)
    robot.spin()


if __name__ == "__main__":
    main()
