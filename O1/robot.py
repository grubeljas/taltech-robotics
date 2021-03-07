"""O1."""
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Constructor for robot."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

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
        print("left lasers")
        print(f"dis {self.left_side} {self.left_diagonal} {self.left_back}")
        print("right lasers")
        print(f"dis {self.right_side} {self.right_diagonal} {self.right_back}")
        print("front lasers")
        print(f"dis {self.fl} {self.fm} {self.fr}")

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        # front 10-100 cm
        self.fl = self.robot.get_front_left_laser()
        self.fm = self.robot.get_front_middle_laser()
        self.fr = self.robot.get_front_right_laser()

        # 2-16 cm
        self.left_back = self.robot.get_rear_left_straight_ir()
        self.left_diagonal = self.robot.get_rear_left_diagonal_ir()
        self.left_side = self.robot.get_rear_left_side_ir()

        self.right_back = self.robot.get_rear_right_straight_ir()
        self.right_diagonal = self.robot.get_rear_right_diagonal_ir()
        self.right_side = self.robot.get_rear_right_side_ir()

    def act(self, left_wheel, right_wheel):
        """."""
        self.robot.set_right_wheel_speed(right_wheel)
        self.robot.set_left_wheel_speed(left_wheel)

    def plan(self):
        """Perform the planning steps as required by the problem statement."""
        if self.fm < 0.55:
            self.act(self.speed, self.speed)
            if self.fm <= 0.1:
                self.ultra_spin()
                self.shutdown = True
        else:
            self.act(-self.speed, self.speed)

    def plan2(self):
        """Perform the planning steps as required by the problem statement."""
        if self.fm < 0.55:
            if self.previous_state == self.state:
                if self.robot.get_right_wheel_encoder() > self.robot.get_left_wheel_encoder():
                    self.l += 1
                if self.robot.get_right_wheel_encoder() < self.robot.get_left_wheel_encoder():
                    self.r += 1
            else:
                self.r = 0
                self.l = 0
            self.act(self.speed + self.l, self.speed + self.r)
            if self.fm <= 0.1:
                self.ultra_spin()
                self.shutdown = True
        else:
            self.act(-self.speed, self.speed)

    def ultra_spin(self):
        """Make a spin on 90 degrees."""
        print("spin")
        self.act(-self.speed, self.speed)
        self.robot.sleep(5)
        self.act(0, 0)

    def spin(self):
        """The main loop of the robot."""
        if self.simulation:
            while not self.shutdown:
                self.sense()
                self.get_state()
                self.plan()
                self.robot.sleep(0.05)
        else:
            while not self.shutdown:
                self.sense()
                self.get_state()
                self.plan2()
                self.robot.sleep(0.05)


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
