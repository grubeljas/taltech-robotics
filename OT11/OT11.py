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
        self.robot_object_angle = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

    def get_x_speed(self, yaw):
        """X coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) \
               * math.cos(yaw)

    def get_y_speed(self, yaw):
        """Y coordinate change in time."""
        return ((self.robot.WHEEL_DIAMETER / 2) / 2 * (self.angularLeftVelocity + self.angularRightVelocity)) \
               * math.sin(yaw)

    def get_yaw(self):
        """Calculate yaw for encoder odometry."""
        return (self.robot.WHEEL_DIAMETER / 2) / self.robot.AXIS_LENGTH \
               * (self.angularRightVelocity - self.angularLeftVelocity)

    def get_encoder_odometry(self):
        """
        Return the encoder odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder data. The units must be (meters, meters, radians).
        """
        self.yaw = self.encoder_odometry[2] + (self.get_yaw() * self.cycle_time)
        self.encoder_odometry = (self.encoder_odometry[0] + (self.get_x_speed(self.yaw) * self.cycle_time),
                                 self.encoder_odometry[1] + (self.get_y_speed(self.yaw) * self.cycle_time), self.yaw)
        return self.encoder_odometry

    def update_world(self) -> None:
        """Update the world model (insert objects into memory)."""
        for item in range(len(self.camera_objects)):

            if self.max_width and len(self.camera_objects) > 0:
                self.rad = math.radians(
                    ((self.max_width / 2 - self.camera_objects[item][1][0]) / self.max_width) * self.field_of_view[0])
                self.rad = self.rad % (math.pi * 2)

            self.object_dist = 30 / self.camera_objects[item][2]
            print(self.object_dist, self.camera_objects[item][2], "_____")


            self.object_x = self.object_dist * math.sin(self.yaw + self.rad)
            self.object_y = self.object_dist * math.cos(self.yaw + self.rad)

            print(self.object_diff_x, self.object_diff_y, self.object_x, self.object_y,
                  self.object_diff_x * math.sin(self.yaw + self.rad),
                  self.object_diff_y * math.cos(self.yaw + self.rad))

            print(self.yaw, "robot YAW", self.rad, "Object yaw from robot")
            self.item_dict[item + len(self.item_dict)] = (self.encoder_odometry[0] + self.object_x,
                                                          self.encoder_odometry[1] + self.object_y)

    @property
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
        for item in self.item_dict:
            self.shortest_dist = 10000
            print("X:", self.item_dict[item][0], self.encoder_odometry[0], "Y:", self.item_dict[item][1], self.encoder_odometry[1])
            self.euclidean_distance = math.sqrt(math.pow(self.item_dict[item][0] - self.encoder_odometry[0], 2) + math.pow(self.item_dict[item][1] - self.encoder_odometry[1], 2))
            if self.euclidean_distance < self.shortest_dist:
                self.shortest_dist = self.euclidean_distance
                self.shortest_point = (self.item_dict[item][0], self.item_dict[item][1])
        if self.shortest_point:
            self.robot_object_angle = math.atan2(self.shortest_point[1] - self.encoder_odometry[1], self.shortest_point[0] - self.encoder_odometry[0])
            print(self.robot_object_angle, self.yaw, "Object angle AND THEN YAW")
            return (self.robot_object_angle - self.yaw) % (2 * math.pi)
        else:
            return None

    def sense(self):
        """SPA architecture sense block."""
        self.camera_objects = self.robot.get_camera_objects()
        self.max_width = self.resolution[0]

        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

        self.time = self.robot.get_time()

        self.cycle_time = self.time - self.last_time
        self.left_cycle_encoder = self.left_encoder - self.left_last_encoder
        self.right_cycle_encoder = self.right_encoder - self.right_last_encoder

        if self.cycle_time > 0:
            self.angularLeftVelocity = ((math.radians(self.left_cycle_encoder) / self.cycle_time))
            self.angularRightVelocity = ((math.radians(self.right_cycle_encoder) / self.cycle_time))
        else:
            self.angularLeftVelocity = 0
            self.angularRightVelocity = 0

        self.truth = self.robot.get_ground_truth()

        self.get_encoder_odometry()
        if not (self.camera_objects == self.camera_objects_copy):
            self.update_world()
            self.camera_objects_copy = self.camera_objects.copy()
            print(self.camera_objects_copy, self.camera_objects, "CAMOBJ")
        print(self.item_dict, "ITEMDICT")
        self.get_closest_object_angle
        print(self.shortest_point, "CLOSEST OBJECT", self.get_closest_object_angle, "ANGLE", self.yaw, "YAW")
        print(self.angularLeftVelocity, self.angularRightVelocity, "velocities")
        print("ENCODER ODO", self.encoder_odometry)
        print("TRUTH", self.truth)

        # new previous values
        self.last_time = self.time
        self.left_last_encoder = self.left_encoder
        self.right_last_encoder = self.right_encoder
        pass

    def spin(self):
        """Spin loop."""
        for _ in range(100):
            self.sense()
            print(f"objects = {self.robot.get_camera_objects()}")
            self.robot.sleep(0.05)


def main():
    """The main entry point."""
    robot = Robot()
    robot.spin()

if __name__ == "__main__":
    main()
