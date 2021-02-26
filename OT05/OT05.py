"""OT05 - Noise."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize object."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.sensor = [0, 0, 0, 0, 0]

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the PiBot reference."""
        self.robot = robot

    def get_front_middle_laser(self) -> None:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        laser_info = self.robot.get_front_middle_laser()
        if laser_info is None:
            return None
        self.sensor.pop(0)
        self.sensor.append(laser_info)
        list = sorted(self.sensor[:], key=lambda x: x)
        return list[2]

    def sense(self):
        self.middle = self.get_front_middle_laser()

    def spin(self):
        """The spin loop."""
        while not self.shutdown:
            self.sense()
            print(f'Value is {self.middle}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def test():
    """Test with info."""
    robot = Robot()
    import dataset1
    data = dataset1.get_data()
    robot.robot.load_data_profile(data)
    for i in range(len(data)):
        print(f"laser = {robot.get_front_middle_laser()}")
        robot.robot.sleep(0.05)


def main():
    """The main entry point."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    test()
