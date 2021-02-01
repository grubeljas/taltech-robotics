import PiBot

class Robot:
    def __init__(self):
        """
        Initialize class.
        """
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.lasers = self.sense()
        SPEEED = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.
        """
        self.robot = robot

    def sense():
        self.get_front_lasers()

    def act():
        self.set_wheels_speed(SPEEED)
        

    def plan():
        if self.lasers[0] > 100:
            SPEEED = 50
        else:
            SPEED = -10

    def spin(self):
        """
        The main loop of the robot.
        This loop is expected to call sense, plan, act methods cyclically.
        """
        while not self.shutdown:
            print(f'The time is {self.robot.get_time()}!')
            self.robot.sleep(0.05)
            self.sense()
            self.plan()
            self.act()
            if self.robot.get_time() > 20:
                self.shutdown = True

    # Add more code...


def main():
    """
    The main function.

    Create a Robot class object and run it.
    """
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
