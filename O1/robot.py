"""O1."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.simulation = self.robot.is_simulation()
        # front lasers
        self.fl = 2
        self.fm = 2
        self.fr = 2

        self.left_side = None
        self.left_diagonal = None
        self.left_back = None

        self.right_back = None
        self.right_side = None
        self.right_diagonal = None

        self.l = 0
        self.r = 0

        self.speed = 8
        self.state = 0 # 0 - left ; 1 - straight
        self.previous_state = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to PiBot object.

        Returns:
          None
        """
        self.robot = robot

    def get_state(self):
        """Return the current state."""
        print("------")
        print(f"{self.r} {self.l}")
        print("front lasers")
        print(f"dis {self.fl} {self.fm} {self.fr}")

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        # front 10-100 cm
        self.fl = self.robot.get_front_left_laser()
        self.fm = self.robot.get_front_middle_laser()
        self.fr = self.robot.get_front_right_laser()

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_right_wheel_speed(right_wheel)
        self.robot.set_left_wheel_speed(left_wheel)

    def straight(self):
        """."""
        if self.previous_state == self.state:
            if self.robot.get_right_wheel_encoder() > self.robot.get_left_wheel_encoder():
                self.r += 1
            if self.robot.get_right_wheel_encoder() < self.robot.get_left_wheel_encoder():
                self.l += 1
        else:
            self.r = 0
            self.l = 0
        self.act(self.speed + self.l, self.speed + self.r)
        if self.state:
            self.previous_state = self.state

        print("object is close")
        if self.fm <= 0.05:
            self.ultra_spin()
            self.shutdown = True

    def turn_left(self):
        """Turn left until object."""
        print("spinning")
        if self.fm < 0.50:
            self.state = 1
            self.previous_state = 0
            self.r = 0
            self.l = 0
            return

        self.act(self.speed + self.l, self.speed + self.r)

    def plan(self):
        """Perform the planning steps as required by the problem statement."""
        if self.state:
            self.straight()
        else:
            self.turn_left()

    def ultra_spin(self):
        """Make a spin on 90 degrees."""
        print("spin")
        self.act(-self.speed, self.speed)
        self.robot.sleep(5)
        self.act(0, 0)

    def spin(self):
        """The main loop of the robot."""
        while not self.shutdown:
            self.sense()
            self.get_state()
            self.plan()
            self.robot.sleep(0.05)


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
