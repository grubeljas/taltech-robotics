"""OT10 - Robot vision processing."""
import PiBot
import math


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize variables."""
        self.robot = PiBot.PiBot()
        self.camera_objects = []
        self.resolution = self.robot.CAMERA_RESOLUTION
        self.field_of_view = self.robot.CAMERA_FIELD_OF_VIEW
        self.closest_object = ["", (0, 0), 0]
        self.current_object = ["", (0, 0), 0]
        self.closest_index = 0
        self.closest_x = 0

        self.max_width = 0
        self.rad = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

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
        if len(self.camera_objects) == 0:
            return None
        for item in range(len(self.camera_objects)):
            self.current_object = self.camera_objects[item]
            if self.current_object[2] > self.closest_object[2]:
                self.closest_object = self.current_object
                self.closest_index = item
                self.closest_x = self.closest_object[1][0]
        if self.max_width and len(self.camera_objects) > 0:
            print(self.field_of_view)
            self.rad = math.radians(((self.max_width / 2 - self.closest_x) / self.max_width) * self.field_of_view[0])
            return self.rad

    def sense(self):
        """SPA architecture sense block."""
        self.camera_objects = self.robot.get_camera_objects()
        self.max_width = self.resolution[0]
        self.get_closest_visible_object_angle()

    def spin(self):
        """The spin loop."""
        for _ in range(100):
            self.sense()
            print(self.robot.get_camera_objects())
            self.robot.sleep(0.05)


def main():
    """Main entry point."""
    robot = Robot()
    import blue_approach
    data = blue_approach.get_data()
    robot.robot.load_data_profile(data)
    robot.spin()


if __name__ == "__main__":
    main()
